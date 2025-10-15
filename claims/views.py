
from django.template.loader import render_to_string
from policies.models import Policy, PolicyHolder
from policies.views import format_money
from .models import Claim
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
import uuid
from .models import Claim, ClaimMedicalInfo, ClaimDocument
from policies.models import Policy
@login_required

def custom_claims_user(request):
    user = request.user

    # Tổng số yêu cầu bồi thường
    total_claims = Claim.objects.filter(policy__customer__user=user).count()

    # Số yêu cầu đã duyệt
    approved_claims = Claim.objects.filter(policy__customer__user=user, claim_status="approved").count()

    # Số yêu cầu chờ xử lý
    pending_claims = Claim.objects.filter(policy__customer__user=user, claim_status="pending").count()
    # Tổng số tiền đã bồi thường

    total_paid = Claim.objects.filter(policy__customer__user=request.user).aggregate(
        total=Sum("claimed_amount")
    )["total"] or 0

    total_paid_display = format_money(total_paid)

    # Danh sách claim theo user
    search_query = request.GET.get("q", "")
    claims = Claim.objects.select_related("policy", "policy__product").filter(policy__customer__user=user)

    # Tìm kiếm
    if search_query:
        claims = claims.filter(
            Q(claim_number__icontains=search_query) |
            Q(policy__policy_number__icontains=search_query) |
            Q(policy__product__product_name__icontains=search_query)
        )

    # Lọc theo trạng thái
    status = request.GET.get("status")
    if status:
        claims = claims.filter(claim_status=status)

    context = {
        "total_claims": total_claims,
        "pending_claims": pending_claims,
        "approved_claims": approved_claims,
        "total_paid": total_paid_display,
        "claims": claims,
        "search_query": search_query,
    }
    return render(request, "claims/claims_user.html",context)

@login_required
def filter_claims_ajax(request):
    user = request.user
    search = request.GET.get("q", "")
    status = request.GET.get("status", "")
    sort = request.GET.get("sort", "newest")

    claims = Claim.objects.select_related("policy", "policy__product").filter(policy__customer__user=user)

    # Lọc
    if status and status != "all":
        claims = claims.filter(claim_status=status)

    # Tìm kiếm
    if search:
        claims = claims.filter(
            Q(claim_number__icontains=search) |
            Q(policy__product__product_name__icontains=search)
        )

    # Sắp xếp
    if sort == "newest":
        claims = claims.order_by("-claim_date")
    elif sort == "oldest":
        claims = claims.order_by("claim_date")
    elif sort == "amount-high":
            claims = claims.order_by("-claimed_amount")
    elif sort == "amount-low":
        claims = claims.order_by("claimed_amount")

    html = render_to_string("claims/claims_list.html", {"claims": claims})
    return JsonResponse({"html": html})

@login_required
def create_claims(request, pk):
    policy = get_object_or_404(Policy, id=pk, customer__user=request.user)
    policyHolder = PolicyHolder.objects.filter(policy=policy).first()
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
            data = request.POST

            # Tạo claim number
            claim_number = f"CLM-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

            # Tạo yêu cầu bồi thường
            claim = Claim.objects.create(
                policy=policy,
                customer=policy.customer,
                claim_number=claim_number,
                incident_date=data.get('incidentDate'),
                description=data.get('description'),
                requested_amount=data.get('totalCost'),  #xem lại
                claim_status='pending'
            )

            # Tạo thông tin y tế
            ClaimMedicalInfo.objects.create(
                claim=claim,
                treatment_type=data.get('treatmentType'),
                hospital_name=data.get('hospitalName'),
                doctor_name=data.get('doctorName'),
                hospital_address=data.get('hospital_address'),
                diagnosis=data.get('diagnosis'),
                admission_date=data.get('admissionDate') or None,
                discharge_date=data.get('dischargeDate') or None,
                total_treatment_cost=data.get('totalCost')
            )

            # Xử lý file upload
            if request.FILES:
                fs = FileSystemStorage()
                document_mapping = {
                    'medicalBill': 'Hóa đơn viện phí',
                    'medicalRecords': 'Hồ sơ bệnh án',
                    'prescription': 'Đơn thuốc',
                    'testResults': 'Kết quả xét nghiệm',
                    'additionalDocs': 'Tài liệu bổ sung'
                }

                for field_name, document_type in document_mapping.items():
                    files = request.FILES.getlist(field_name)
                    for file in files:
                        filename = fs.save(f'claims/claim_{claim.id}/{file.name}', file)
                        file_url = fs.url(filename)

                        ClaimDocument.objects.create(
                            claim=claim,
                            document_type=document_type,
                            file_url=file_url
                        )

            return JsonResponse({
                'success': True,
                'claim_id': claim.claim_number,
                'message': 'Gửi yêu cầu bồi thường thành công!'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Có lỗi xảy ra: {str(e)}'
            })

    context = {
        "policy": policy,
        "policyHolder": policyHolder,
        'treatment_types': ClaimMedicalInfo.TREATMENT_TYPE_CHOICES
    }
    return  render(request, "claims/create_claims.html", context)