from decimal import Decimal

from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from policies.models import PolicyHolder
from policies.views import format_money

from .models import ClaimPayment, RiskAssessment
from django.db.models import Sum, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
import uuid
from .models import Claim, ClaimMedicalInfo, ClaimDocument
from policies.models import Policy
# USER
@login_required(login_url='login')
def custom_claims_user(request):
    user = request.user

    # Tổng số yêu cầu bồi thường
    total_claims = Claim.objects.filter(policy__customer__user=user).count()

    # Số yêu cầu đã duyệt
    approved_claims = Claim.objects.filter(policy__customer__user=user, claim_status="approved").count()

    # Số yêu cầu chờ xử lý
    pending_claims = Claim.objects.filter(policy__customer__user=user, claim_status="pending").count()
    # Tổng số tiền đã bồi thường
    total_paid = Policy.objects.filter(customer__user=request.user).aggregate(
        total=Sum("claimed_amount")
    )["total"] or 0

    total_paid_display = format_money(total_paid)
    claims = (Claim.objects.select_related("policy", "policy__product")
                    .prefetch_related("claim_medical_info", "claim_documents")
                    .filter(policy__customer__user=user
    ).order_by("-claim_date"))
    # Phân trang mặc định
    paginator = Paginator(claims, 5)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(request, "claims/user/claims_user.html", {
        "claims": page_obj.object_list,
        "page_obj": page_obj,
        "total_claims": total_claims,
        "approved_claims": approved_claims,
        "pending_claims": pending_claims,
        "total_paid": total_paid_display,

    })

@login_required(login_url='login')
def filter_claims_ajax(request):
    user = request.user
    search = request.GET.get("q", "")
    status = request.GET.get("status", "")
    sort = request.GET.get("sort", "newest")
    page_number = request.GET.get("page", 1)


    claims = (Claim.objects.select_related("policy", "policy__product")
                    .prefetch_related("claim_medical_info", "claim_documents")
                    .filter(policy__customer__user=user
    ).order_by("-claim_date"))

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
        claims = claims.order_by("-approved_amount")
    elif sort == "amount-low":
        claims = claims.order_by("approved_amount")
    # --- Phân trang ---
    paginator = Paginator(claims, 4)
    page_obj = paginator.get_page(page_number)

    print("số page= ",page_obj.paginator.num_pages)
    html = render_to_string(
        "claims/user/claims_list.html",
        {"claims": page_obj.object_list, "page_obj": page_obj,},
    )
    return JsonResponse({"html": html})

@login_required(login_url='login')
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

@login_required(login_url='login')
def detail_claims(request,pk):
    """
    Hiển thị chi tiết yêu cầu bồi thường
    """
    try:
        claim = get_object_or_404(
            Claim.objects.select_related('policy'),
            id=pk
        )
        # Kiểm tra quyền truy cập
        if claim.policy.customer.user != request.user:
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

from django.utils import timezone

def generate_timeline(claim):
    """
    Sinh timeline hiển thị tiến trình xử lý yêu cầu bồi thường
    theo trạng thái hiện tại của claim.
    """

    timeline = []

    # STEP 1️⃣: Nộp yêu cầu
    timeline.append({
        'step': 1,
        'title': 'Đã nộp yêu cầu',
        'description': 'Khách hàng đã gửi yêu cầu bồi thường.',
        'date': claim.claim_date.strftime('%d/%m/%Y - %H:%M'),
        'status': 'completed',
        'icon': 'fa-file-upload'
    })

    # STEP 2️⃣: Kiểm tra tài liệu
    if claim.claim_status in ['in_progress', 'approved', 'rejected', 'request_more', 'settled']:
        status = 'completed'
        date = 'Đã xử lý'
    elif claim.claim_status == 'pending':
        status = 'in_progress'
        date = 'Đang xử lý'
    else:
        status = 'pending'
        date = 'Chờ xử lý'

    timeline.append({
        'step': 2,
        'title': 'Kiểm tra tài liệu',
        'description': 'Tài liệu được nhân viên xác minh và đánh giá.',
        'date': date,
        'status': status,
        'icon': 'fa-folder-open'
    })

    # STEP 3️⃣: Đánh giá yêu cầu
    if claim.claim_status == 'in_progress':
        status = 'in_progress'
        date = 'Đang xử lý'
    elif claim.claim_status in ['approved', 'rejected', 'request_more', 'settled']:
        status = 'completed'
        date = 'Đã xử lý'
    else:
        status = 'pending'
        date = 'Chờ xử lý'

    timeline.append({
        'step': 3,
        'title': 'Đánh giá yêu cầu',
        'description': 'Bộ phận chuyên môn đang xem xét chi tiết yêu cầu bồi thường.',
        'date': date,
        'status': status,
        'icon': 'fa-search'
    })

    # STEP 4️⃣: Quyết định phê duyệt / từ chối / yêu cầu bổ sung
    if claim.claim_status in ['approved', 'rejected', 'request_more', 'settled']:
        status = 'completed'
        date = 'Đã xử lý'
    elif claim.claim_status == 'in_progress':
        status = 'in_progress'
        date = 'Đang xử lý'
    else:
        status = 'pending'
        date = 'Chờ xử lý'

    # Biểu tượng & mô tả linh hoạt theo loại quyết định
    desc_map = {
        'approved': 'Yêu cầu bồi thường đã được phê duyệt.',
        'rejected': 'Yêu cầu bồi thường đã bị từ chối.',
        'request_more': 'Yêu cầu khách hàng bổ sung thêm tài liệu.',
        'in_progress': 'Đang chờ quyết định cuối cùng.',
        'pending': 'Đang chờ xử lý.'
    }

    icon_map = {
        'approved': 'fa-check-circle',
        'rejected': 'fa-times-circle',
        'request_more': 'fa-exclamation-circle',
        'in_progress': 'fa-hourglass-half',
        'pending': 'fa-clipboard-list'
    }

    timeline.append({
        'step': 4,
        'title': 'Quyết định xử lý',
        'description': desc_map.get(claim.claim_status, 'Đang xử lý yêu cầu.'),
        'date': date,
        'status': status,
        'icon': icon_map.get(claim.claim_status, 'fa-clipboard-list')
    })

    # STEP 5️⃣: Thanh toán bồi thường
    if claim.claim_status == 'settled':
        status = 'completed'
        date = claim.settlement_date.strftime('%d/%m/%Y - %H:%M') if claim.settlement_date else 'Đã giải quyết'
    elif claim.claim_status == 'approved':
        status = 'in_progress'
        date = 'Đang tiến hành thanh toán'
    else:
        status = 'pending'
        date = 'Chờ phê duyệt'

    timeline.append({
        'step': 5,
        'title': 'Thanh toán',
        'description': 'Thực hiện thanh toán số tiền bồi thường cho khách hàng.',
        'date': date,
        'status': status,
        'icon': 'fa-money-bill-wave'
    })

    return timeline

@login_required(login_url='login')
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

# ADMIN
@login_required(login_url='login')
def custom_claims_admin(request):
    # Số yeeu cầu từ chối
    rejected_claims = Claim.objects.filter( claim_status="rejected").all().count()

    # Số yêu cầu đã duyệt
    approved_claims = Claim.objects.filter( claim_status="approved").all().count()

    # Số yêu cầu chờ xử lý
    pending_claims = Claim.objects.filter( claim_status="pending").all().count()
    # Tổng số tiền đã bồi thường
    total_paid = Policy.objects.all().aggregate(
        total=Sum("claimed_amount")
    )["total"] or 0

    total_paid_display = format_money(total_paid)
    claims = Claim.objects.select_related("policy", "policy__product").prefetch_related("claim_medical_info", "claim_documents").order_by("-claim_date")


    return render(request, "claims/admin/claim_home.html", {
        "rejected_claims": rejected_claims,
        "approved_claims": approved_claims,
        "pending_claims": pending_claims,
        "total_paid": total_paid_display,
        "status_choices": Claim.CLAIM_STATUS_CHOICES,
        "type_choices": ClaimMedicalInfo.TREATMENT_TYPE_CHOICES,
    })

@csrf_exempt
@require_http_methods(["GET"])
def get_all_claims(request):
    """Lấy danh sách yêu cầu bồi thường có lọc, tìm kiếm và phân trang"""
    search = request.GET.get("search", "").strip()
    status_filter = request.GET.get("status", "").strip()
    page = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("page_size", 10))

    # 🔍 Tìm kiếm
    claims = (
        Claim.objects
        .select_related( "policy")
        .prefetch_related("claim_medical_info", "claim_documents")
        .all()
    )

    if search:
        claims = claims.filter(
            Q(claim_number__icontains=search)
            | Q(policy__customer__user__first_name__icontains=search)
            | Q(policy__customer__user__last_name__icontains=search)
            | Q(policy__policy_number__icontains=search)
        )

    # ⚙️ Lọc theo trạng thái
    if status_filter:
        claims = claims.filter(claim_status=status_filter)
    # 🔢 Phân trang
    paginator = Paginator(claims.order_by("-created_at"), page_size)
    page_obj = paginator.get_page(page)

    data = [
        {
            "id": claim.id,
            "claim_number": claim.claim_number,
            "policy": claim.policy.policy_number if claim.policy else None,
            "customer_name": claim.policy.customer.user.get_full_name(),
            "incident_date": claim.incident_date,
            "requested_amount": float(claim.requested_amount),
            "product_name":claim.policy.product.product_name,
            "claim_status": claim.claim_status,
            "description":claim.description,
            "created_at": claim.created_at.strftime("%Y-%m-%d %H:%M"),

            "medical_info": [
                {
                    "hospital_name": info.hospital_name,
                    "treatment_type": info.treatment_type,
                    "diagnosis": info.diagnosis,
                    "doctor_name": info.doctor_name,
                    "hospital_address":info.hospital_address,
                    "admission_date":info.admission_date,
                    "discharge_date":info.discharge_date,
                    "total_treatment_cost":info.total_treatment_cost
                }
                for info in claim.claim_medical_info.all()
            ],

            "documents_count": claim.claim_documents.count(),
            "documents": [
                {

                    "document_type": doc.document_type,
                    "file_url": doc.file_url.url if doc.file_url else None,
                    "uploaded_at": doc.uploaded_at.strftime("%Y-%m-%d %H:%M"),
                }
                for doc in claim.claim_documents.all()
            ],
        }
        for claim in page_obj
    ]

    return JsonResponse(
        {
            "claims": data,
            "pagination": {
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_size": page_size,
            },
        },
        status=200,
    )
def assess_claim_risk(claim):
    """
    Đánh giá rủi ro gian lận yêu cầu bồi thường.
    """
    score = 0
    details = {}

    medical_info = claim.claim_medical_info.first()

    # 1️ Kiểm tra loại điều trị và số tiền yêu cầu
    if medical_info:
        treatment_type = medical_info.treatment_type
        amount = claim.requested_amount

        # Ngoại trú: chi phí cao bất thường
        if treatment_type == "outpatient" and amount > 10_000_000:
            score += 25
            details["outpatient_high_cost"] = "Điều trị ngoại trú nhưng chi phí > 10 triệu"

        # Nội trú: chi phí quá thấp hoặc quá cao
        elif treatment_type == "inpatient":
            if amount < 500_000:
                score += 15
                details["inpatient_low_cost"] = "Điều trị nội trú nhưng chi phí bất thường thấp"
            elif amount > 100_000_000:
                score += 30
                details["inpatient_high_cost"] = "Điều trị nội trú với chi phí rất cao"

        # Phẫu thuật: yêu cầu bồi thường nhiều lần hoặc số tiền vượt trội
        elif treatment_type == "surgery":
            if amount > 200_000_000:
                score += 40
                details["surgery_unusual_cost"] = "Phẫu thuật có chi phí cực cao"
            if claim.customer.claim_set.filter(claim_medical_info__treatment_type="surgery").count() > 2:
                score += 20
                details["multiple_surgeries"] = "Khách hàng có nhiều yêu cầu phẫu thuật trong thời gian ngắn"

        # Khám sức khỏe: nhưng lại yêu cầu bồi thường lớn (bất thường)
        elif treatment_type == "checkup" and amount > 1_000_000:
            score += 15
            details["checkup_high_cost"] = "Khám sức khỏe mà yêu cầu chi phí cao"

    # 2️ Kiểm tra thời gian yêu cầu sau khi mua bảo hiểm
    if (claim.incident_date - claim.policy.start_date).days < 30:
        score += 25
        details["early_claim"] = "Phát sinh yêu cầu sớm trong vòng 30 ngày kể từ ngày hiệu lực"

    # 3️ Nếu khách hàng đã từng bị từ chối trước đó
    if claim.customer.claim_set.filter(claim_status="rejected").exists():
        score += 10
        details["previous_rejection"] = "Khách hàng từng có yêu cầu bị từ chối"

    # 4️⃣ Nếu có thiếu tài liệu
    if claim.claim_documents.count() < 2:
        score += 10
        details["missing_documents"] = "Thiếu tài liệu bồi thường cần thiết"
    if score <= 30:
        level = "low"
        level_display = "Thấp"
    elif score <= 60:
        level = "medium"
        level_display = "Trung bình"
    else:
        level = "high"
        level_display = "Cao"
    return {"risk_level": level, "score": score, "details": details,"risk_level_display": level_display}
@login_required
@require_http_methods(["GET"])
def claim_risk_assessment_api(request, claim_id):
    """
    API đánh giá rủi ro gian lận của hồ sơ bồi thường
    """
    try:
        claim = Claim.objects.get(id=claim_id)
        claim.status = "in_progress"
        claim.save()
    except Claim.DoesNotExist:
        return JsonResponse(
            {"error": "Không tìm thấy hồ sơ bồi thường"}, status=404
        )

    result = assess_claim_risk(claim)
    # RiskAssessment.objects.create(
    #     claim=claim,
    #     policy=claim.policy,
    #     risk_score=result["score"],
    #     risk_level=result["risk_level"],
    #     ai_model_version="v1.0",
    #     assessment_details=result["details"],
    # )
    return JsonResponse(result, status=200, safe=False)
@login_required
def claim_decision_view(request, claim_id):
    """
    Xử lý phê duyệt / từ chối / yêu cầu bổ sung bồi thường
    """
    claim = get_object_or_404(Claim, id=claim_id)

    if request.method == "POST":
        decision = request.POST.get("decision")
        reason = request.POST.get("reason")
        approvedAmount = request.POST.get("approvedAmount")
        if not decision or not reason:
            messages.error(request, "Vui lòng chọn quyết định và nhập lý do.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        # Cập nhật quyết định
        if decision == "approve":
            claim.approved(request.user, reason,approvedAmount)
            messages.success(request, "✅ Đã phê duyệt yêu cầu bồi thường.")
        elif decision == "reject":
            claim.reject(request.user, reason)
            messages.warning(request, "❌ Đã từ chối yêu cầu bồi thường.")
        elif decision == "request_more":
            claim.request_more(request.user, reason)
            messages.info(request, "🟡 Đã yêu cầu bổ sung tài liệu.")
        else:
            messages.error(request, "Giá trị quyết định không hợp lệ.")
            return redirect(request.META.get("HTTP_REFERER", "/"))
        send_mail(
            subject=f"Kết quả xử lý bồi thường #{claim.id}",
            message=f"Kính gửi {claim.customer.user.get_full_name()},\n\n"
                    f"Yêu cầu bồi thường của bạn đã được xử lý: {claim.get_claim_status_display()}.\n"
                    f"Lý do: {reason}\n\nTrân trọng,\nCông ty bảo hiểm",
            from_email="noreply@insurance.vn",
            recipient_list=[claim.customer.user.email],
        )

    print(claim.get_claim_status_display())
    # Nếu GET thì chỉ hiển thị thông tin
    return JsonResponse({
        "claim_id": claim.id,
        "claim_status": claim.claim_status,
        "reason": claim.decision_reason,
        "decided_by": claim.decided_by.username if claim.decided_by else None,
        "settlement_date": claim.settlement_date,
    })