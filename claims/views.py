from django.contrib import messages
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from policies.models import PolicyHolder
from policies.views import format_money

from .models import ClaimPayment
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
    claims = Claim.objects.select_related("policy", "policy__product").filter(
        policy__customer__user=user
    ).order_by("-claim_date")
    # Phân trang mặc định
    paginator = Paginator(claims, 5)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(request, "claims/user/claims_user.html", {
        "claims": page_obj.object_list,
        "page_obj": page_obj
    })



@login_required
def filter_claims_ajax(request):
    user = request.user
    search = request.GET.get("q", "")
    status = request.GET.get("status", "")
    sort = request.GET.get("sort", "newest")
    page_number = request.GET.get("page", 1)

    claims = Claim.objects.select_related("policy", "policy__product").filter(
        policy__customer__user=user
    )

    # --- Lọc ---
    if status and status != "all":
        claims = claims.filter(claim_status=status)

    # --- Tìm kiếm ---
    if search:
        claims = claims.filter(
            Q(claim_number__icontains=search)
            | Q(policy__product__product_name__icontains=search)
        )

    # --- Sắp xếp ---
    if sort == "newest":
        claims = claims.order_by("-claim_date")
    elif sort == "oldest":
        claims = claims.order_by("claim_date")
    elif sort == "amount-high":
        claims = claims.order_by("-claimed_amount")
    elif sort == "amount-low":
        claims = claims.order_by("claimed_amount")
    # --- Phân trang ---
    paginator = Paginator(claims, 4)
    page_obj = paginator.get_page(page_number)

    print("số page= ",page_obj.paginator.num_pages)
    html = render_to_string(
        "claims/user/claims_list.html",
        {"claims": page_obj.object_list, "page_obj": page_obj}
    )
    return JsonResponse({"html": html})

@login_required
def create_claims(request, pk):
    policy = get_object_or_404(Policy, id=pk, customer__user=request.user)
    policyHolder = PolicyHolder.objects.filter(policy=policy).first()
    #  Chỉ cho phép hợp đồng đang hoạt động
    if policy.policy_status != "active":
        messages.error(request,"Hợp đồng của bạn chưa hoạt động hoặc đã hết hạn, không thể gửi yêu cầu bồi thường.")
        return redirect('custom_policies_users')
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
                requested_amount=data.get('requested_amount'),
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
            # Tạo thông tin nhận tiền bồi thường
            ClaimPayment.objects.create(
                claim=claim,
                bank_name=data.get('bankName'),
                account_number=data.get('accountNumber'),
                account_holder_name=data.get('accountHolderName'),
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
                        ClaimDocument.objects.create(
                            claim=claim,
                            document_type=document_type,
                            file_url=filename
                        )

            return JsonResponse({
                'success': True,
                'claim_id': claim.id,
                'claim_number': claim.claim_number,
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
    return  render(request, "claims/user/create_claims.html", context)

@login_required
def detail_claims(request,pk):
    """
    Hiển thị chi tiết yêu cầu bồi thường
    """
    try:
        claim = get_object_or_404(
            Claim.objects.select_related('policy', 'customer', 'customer__user'),
            id=pk
        )
        # Kiểm tra quyền truy cập
        if claim.customer.user != request.user:
            return render(request, 'errors/403.html', status=403)

        # Lấy thông tin y tế
        claim_medical_info = ClaimMedicalInfo.objects.filter(claim=claim).first()

        # Lấy tài liệu
        claim_documents = ClaimDocument.objects.filter(claim=claim).all()
        timeline = generate_timeline(claim)
        # Lấy thông tin nhận tiền
        claim_payment = ClaimPayment.objects.filter(claim=claim).first()
        context = {
            'claim': claim,
            'medical_info': claim_medical_info,
            'documents': claim_documents,
            'claim_payment': claim_payment,
            'timeline': timeline,
        }

        return render(request, "claims/user/detail_claims.html", context)

    except Claim.DoesNotExist:
        return render(request, 'errors/404.html', status=404)

def generate_timeline(claim):
    """
    Tạo timeline dựa trên trạng thái và thời gian của claim
    """
    timeline = []

    # Step 1: Submitted - Luôn có
    timeline.append({
        'step': 1,
        'title': 'Đã nộp yêu cầu',
        'description': 'Yêu cầu bồi thường đã được gửi thành công',
        'date': claim.claim_date.strftime('%d/%m/%Y - %H:%M'),
        'status': 'completed',
        'icon': 'fa-check'
    })

    # Step 2: Document Review
    doc_status = 'completed' if claim.claim_status in ['in_progress', 'approved', 'settled'] else 'pending'
    doc_date = (claim.claim_date + timezone.timedelta(days=1)).strftime(
        '%d/%m/%Y - %H:%M') if doc_status == 'completed' else 'Đang xử lý'

    timeline.append({
        'step': 2,
        'title': 'Kiểm tra tài liệu',
        'description': 'Tài liệu đã được kiểm tra và xác thực' if doc_status == 'completed' else 'Đang kiểm tra tính hợp lệ của tài liệu',
        'date': doc_date,
        'status': doc_status,
        'icon': 'fa-check' if doc_status == 'completed' else 'fa-search'
    })

    # Step 3: Assessment
    assessment_status = 'pending'
    assessment_date = 'Chờ xử lý'

    if claim.claim_status == 'in_progress':
        assessment_status = 'in_progress'
        assessment_date = (claim.claim_date + timezone.timedelta(days=2)).strftime('%d/%m/%Y - %H:%M')
    elif claim.claim_status in ['approved', 'settled']:
        assessment_status = 'completed'
        assessment_date = (claim.claim_date + timezone.timedelta(days=2)).strftime('%d/%m/%Y - %H:%M')

    timeline.append({
        'step': 3,
        'title': 'Đánh giá yêu cầu',
        'description': 'Chuyên viên đang đánh giá và tính toán số tiền bồi thường' if assessment_status == 'in_progress' else 'Đánh giá chi tiết yêu cầu bồi thường',
        'date': assessment_date,
        'status': assessment_status,
        'icon': 'fa-search' if assessment_status == 'in_progress' else (
            'fa-check' if assessment_status == 'completed' else 'fa-clipboard-list')
    })

    # Step 4: Approval - Luôn có
    approval_status = 'pending'
    approval_date = 'Chờ xử lý'

    if claim.claim_status in ['approved', 'settled']:
        approval_status = 'completed'
        approval_date = (claim.claim_date + timezone.timedelta(days=4)).strftime('%d/%m/%Y - %H:%M')

    timeline.append({
        'step': 4,
        'title': 'Phê duyệt',
        'description': 'Quyết định cuối cùng về yêu cầu bồi thường',
        'date': approval_date,
        'status': approval_status,
        'icon': 'fa-clipboard-check'
    })

    # Step 5: Payment - Luôn có
    payment_status = 'pending'
    payment_date = 'Chờ xử lý'

    if claim.claim_status == 'settled' and claim.settlement_date:
        payment_status = 'completed'
        payment_date = claim.settlement_date.strftime('%d/%m/%Y - %H:%M')
    elif claim.claim_status == 'approved':
        payment_status = 'in_progress'
        payment_date = 'Đang xử lý'

    timeline.append({
        'step': 5,
        'title': 'Thanh toán',
        'description': 'Chuyển khoản số tiền bồi thường',
        'date': payment_date,
        'status': payment_status,
        'icon': 'fa-money-bill-wave'
    })

    return timeline

@login_required
def add_additional_documents(request, claim_number):
    if request.method == 'POST':
        claim = get_object_or_404(Claim, claim_number=claim_number)

        # Kiểm tra quyền truy cập
        if claim.customer.user != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        files = request.FILES.getlist('documents')
        document_type = request.POST.get('document_type', 'additional')
        notes = request.POST.get('notes', '')
        fs = FileSystemStorage()
        added_documents = []
        for file in files:
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                continue
            filename = fs.save(f'claims/claim_{claim.id}/{file.name}', file)
            document = ClaimDocument.objects.create(
                claim=claim,
                document_type=document_type,
                file_url=filename
            )
            added_documents.append({
                'id': document.id,
                'claim_number': claim.claim_number,
                'name': file.name,
                'type': document_type,
                'size': file.size
            })

        return JsonResponse({
            'success': True,
            'message': f'Đã thêm {len(added_documents)} tài liệu mới thành công!',
            'documents': added_documents
        })

    return JsonResponse({'error': 'Method not allowed'}, status=405)