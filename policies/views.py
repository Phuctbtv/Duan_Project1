from datetime import timedelta

from django.core.mail import send_mail
from django.core.paginator import Paginator
import json

from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from insurance_app import settings
from notifications.models import Notification
from payments.models import Payment
from users.models import Agent

from .models import Policy, PolicyHolder, HealthInfo
from .forms import PolicyForm
from insurance_products.models import InsuranceProduct


@login_required
def custom_policies_admin(request):
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    product = request.GET.get('product', '')
    status_choices = Policy.POLICY_STATUS_CHOICES
    # Lấy tất cả sản phẩm từ CSDL để hiển thị dropdown
    products = InsuranceProduct.objects.all()

    # Lấy tất cả hợp đồng + join với customer và product
    policies = Policy.objects.select_related('customer', 'product').prefetch_related('payments').order_by('-created_at').all()
    agent = Agent.objects.all()
    # Cập nhật trạng thái expired nếu end_date < hôm nay
    today = timezone.now().date()
    for policy in policies:
        if policy.end_date and policy.end_date < today and policy.policy_status != "expired":
            policy.policy_status = "expired"
            policy.save(update_fields=["policy_status"])

    # Filter theo tìm kiếm
    if query:
        policies = policies.filter(
            Q(policy_number__icontains=query) |
            Q(product__product_name__icontains=query)
        )
    if status and status != '':
        policies = policies.filter(policy_status=status)
    if product and product != '':
        policies = policies.filter(product__product_name__icontains=product)



    # ======= PHÂN TRANG =======
    paginator = Paginator(policies, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # dashboard
    dashboard_policy= {
        "pending": Policy.objects.filter(policy_status="pending").count(),
        "active": Policy.objects.filter(policy_status="active").count(),
        "cancelled": Policy.objects.filter(policy_status="cancelled").count(),
    }
    context = {
        'policies': page_obj,
        'products': products,
        'query': query,
        'status': status,
        'selected_product': product,
        'dashboard_policy': dashboard_policy,
        'status_choices' : status_choices,
        'agents': agent,

    }
    return render(request, 'admin/policies_section.html', context)


@login_required
def dashboard_view_user(request):
    user = request.user

    # PHÂN BIỆT THEO USER_TYPE
    if user.user_type == 'agent':
        # 🛠 SỬA LỖI: Lấy Agent object từ User
        try:
            agent_obj = Agent.objects.get(user=user)
        except Agent.DoesNotExist:
            #  QUAN TRỌNG: Phải return HttpResponse, không được để None
            context = {
                "total_contracts": 0,
                "active_contracts": 0,
                "year_fee": format_money(0),
                "total_insurance": format_money(0),
                "total_commission": format_money(0),
                "policies": [],
                "search_query": "",
                "status": "",
                "user_type": user.user_type,
                "error_message": "Agent profile not found. Please complete your agent profile."
            }
            return render(request, "policy/policies_users.html", context)

        # THỐNG KÊ CHO AGENT - DÙNG agent_obj
        total_contracts = Policy.objects.filter(agent=agent_obj).count()
        active_contracts = Policy.objects.filter(agent=agent_obj, policy_status="active").count()
        year_fee = Policy.objects.filter(agent=agent_obj).aggregate(total=Sum("premium_amount"))["total"] or 0
        year_fee_display = format_money(year_fee)
        total_insurance = Policy.objects.filter(agent=agent_obj).aggregate(total=Sum("sum_insured"))["total"] or 0
        total_insurance_display = format_money(total_insurance)
        total_commission = Policy.objects.filter(agent=agent_obj, policy_status="active").aggregate(
            total=Sum("commission_amount")
        )["total"] or 0
        total_commission_display = format_money(total_commission)

        # QuerySet cho agent
        policies_qs = Policy.objects.select_related("product", "customer", "customer__user").filter(
            agent=agent_obj
        ).order_by('-updated_at')

    else:
        #  THỐNG KÊ CHO CUSTOMER
        total_contracts = Policy.objects.filter(customer__user_id=user.id).count()
        active_contracts = Policy.objects.filter(customer__user=user, policy_status="active").count()
        year_fee = Policy.objects.filter(customer__user=user).aggregate(total=Sum("premium_amount"))["total"] or 0
        year_fee_display = format_money(year_fee)
        total_insurance = Policy.objects.filter(customer__user=user).aggregate(total=Sum("sum_insured"))["total"] or 0
        total_insurance_display = format_money(total_insurance)
        total_commission = 0
        total_commission_display = format_money(total_commission)

        # QuerySet cho customer
        policies_qs = Policy.objects.select_related("product").filter(
            customer__user=user
        ).order_by('-updated_at')

    # --- Lọc và tìm kiếm (dùng chung) ---
    search_query = request.GET.get("q", "")
    status = request.GET.get("status")

    if search_query:
        policies_qs = policies_qs.filter(
            Q(policy_number__icontains=search_query) |
            Q(product__product_name__icontains=search_query)
        )
    if status:
        policies_qs = policies_qs.filter(policy_status=status)

    # --- Phân trang ---
    page_number = request.GET.get("page", 1)
    paginator = Paginator(policies_qs, 5)
    page_obj = paginator.get_page(page_number)

    context = {
        "total_contracts": total_contracts,
        "active_contracts": active_contracts,
        "year_fee": year_fee_display,
        "total_insurance": total_insurance_display,
        "total_commission": total_commission_display,
        "policies": page_obj,
        "search_query": search_query,
        "status": status,
        "user_type": user.user_type,
    }

    return render(request, "policy/policies_users.html", context)

def format_money(value):
    """Format số tiền: 2000000 -> 2M, 2100000 -> 2.1M"""
    value = float(value or 0)
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}".rstrip("0").rstrip(".") + "M"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}".rstrip("0").rstrip(".") + "K"
    return str(int(value))

@login_required
def admin_policy_list(request):
    """Danh sách + tìm kiếm hợp đồng"""

    # Cập nhật trạng thái hết hạn
    now = timezone.now().date()
    expired_policies = Policy.objects.filter(end_date__lt=now, policy_status="active")
    expired_policies.update(policy_status="expired")

    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    product = request.GET.get('product', '')

    policies = Policy.objects.select_related('customer', 'product').all()

    if query:
        policies = policies.filter(policy_number__icontains=query)
    if status and status != 'Tất cả trạng thái':
        policies = policies.filter(policy_status=status)
    if product and product != 'Tất cả sản phẩm':
        policies = policies.filter(product__product_name=product)

    context = {
        'policies': policies,
        'query': query,
        'status': status,
        'product': product,
    }
    return render(request, 'admin/policies_section.html', context)

@login_required
def admin_policy_detail(request, pk):
    """Xem chi tiết hợp đồng (policy)"""
    policy = get_object_or_404(Policy, pk=pk)
    policyHolder = PolicyHolder.objects.filter(policy=policy).first()
    context = {
        'policy': policy,
        'now': timezone.now(),
        'policyHolder': policyHolder,
    }

    if request.user.is_staff:
        return render(request, 'admin/policies_detail.html', context)
    else:
        return render(request, 'policy/policies_detail.html', context)


@csrf_exempt
@require_GET
def api_policy_detail(request, pk):
    """API lấy chi tiết hợp đồng cho modal"""
    try:
        policy = get_object_or_404(Policy, pk=pk)

        policy_holder = PolicyHolder.objects.filter(policy=policy).first()

        # Lấy thông tin khách hàng
        customer = policy.customer

        user = customer.user

        # Lấy thông tin sức khỏe gần nhất
        health_info = HealthInfo.objects.filter(policy_holder=policy_holder).first()

        # Kiểm tra thanh toán
        payment = Payment.objects.filter(policy=policy, status='success').first()
        payment_status = 'success' if payment else 'pending'

        # Format dữ liệu để trả về JSON
        policy_data = {
            'id': policy.id,
            'policy_number': policy.policy_number,
            'product': {
                'product_name': policy.product.product_name,
            },
            'premium_amount': float(policy.premium_amount),
            'start_date': policy.start_date.isoformat() if policy.start_date else None,
            'end_date': policy.end_date.isoformat() if policy.end_date else None,
            'created_at': policy.created_at.isoformat(),
            'policy_status': policy.policy_status,
            'customer': {
                'user': {
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'email': user.email or '',
                    'phone_number': user.phone_number or '',
                    'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
                    'address': user.address or '',
                },
                'id_card_number': customer.id_card_number or '',
                'gender': customer.gender or '',
                'job': customer.job or '',
                'nationality': customer.nationality or '',

            },
            'health_info': {
                'height': health_info.height if health_info else None,
                'weight': health_info.weight if health_info else None,
                'smoker': health_info.smoker if health_info else 'never',
                'alcohol': health_info.alcohol if health_info else 'no',
                'conditions': health_info.conditions if health_info else [],
            },
            'payment_status': payment_status,
            'policy_holder': {
                'full_name': policy_holder.full_name if policy_holder else None,
                'id_card_number': policy_holder.id_card_number if policy_holder else None,
                'relationship': policy_holder.relationship_to_customer if policy_holder else None,
                'cccd_front': policy_holder.cccd_front.url if policy_holder.cccd_front else None,
                'cccd_back': policy_holder.cccd_back.url if policy_holder.cccd_back else None,
                'selfie': policy_holder.selfie.url if policy_holder.selfie else None,
                'health_certificate': policy_holder.health_certificate.url if policy_holder.health_certificate else None,
            },
        }


        return JsonResponse({
            'success': True,
            'policy': policy_data
        })

    except Exception as e:
        import traceback
        print(f"=== ERROR: {str(e)} ===")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
@login_required
def admin_policy_renew(request, pk):
    """Gia hạn hợp đồng - cập nhật bản ghi cũ"""
    policy = get_object_or_404(Policy, pk=pk)
    if request.method == 'POST':
        # Tính số ngày hợp đồng hiện tại
        duration = policy.end_date - policy.start_date

        # Cập nhật ngày mới
        policy.start_date = policy.end_date + timedelta(days=1)
        policy.end_date = policy.start_date + duration

        policy.policy_status = "active"
        policy.save()

        messages.success(request, f"Hợp đồng {policy.policy_number} đã được gia hạn thành công!")
        return redirect('policy_detail', pk=policy.pk)

    return render(request, 'admin/policies_confirm_renew.html', {'old_policy': policy})


@login_required
def admin_policy_cancel(request, pk):
    """Hủy hợp đồng"""
    policy = get_object_or_404(Policy, pk=pk)
    if request.method == 'POST':
        policy.policy_status = "cancelled"
        policy.save()
        messages.warning(request, f"Hợp đồng {policy.policy_number} đã bị hủy.")
        return redirect('policy_detail', pk=policy.pk)
    return render(request, 'admin/policies_confirm_cancel.html', {'policy': policy})


@login_required
def admin_policy_edit(request, pk):
    """Chỉnh sửa hợp đồng"""
    policy = get_object_or_404(Policy, pk=pk)

    if request.method == 'POST':
        form = PolicyForm(request.POST, instance=policy)
        if form.is_valid():
            # Validate ngày hiệu lực và ngày hết hạn
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            if start_date and end_date:
                if start_date >= end_date:
                    form.add_error('start_date', 'Ngày hiệu lực phải trước ngày hết hạn')
                    form.add_error('end_date', 'Ngày hết hạn phải sau ngày hiệu lực')
                    return render(request, 'admin/policies_form.html', {
                        'form': form,
                        'policy': policy,
                        'title': f'Chỉnh sửa Hợp Đồng - {policy.policy_number}',
                        'action': 'edit'
                    })

            form.save()
            messages.success(request, f"Hợp đồng {policy.policy_number} đã được cập nhật thành công!")
            return redirect('policy_detail', pk=policy.pk)
        else:
            messages.error(request, "Vui lòng sửa các lỗi dưới đây.")
    else:
        form = PolicyForm(instance=policy)

    context = {
        'form': form,
        'policy': policy,
        'title': f'Chỉnh sửa Hợp Đồng - {policy.policy_number}',
        'action': 'edit'
    }
    return render(request, 'admin/policies_form.html', context)



def api_approve_policy(request, pk):
    try:
        policy = get_object_or_404(Policy, pk=pk)
        data = json.loads(request.body)
        note = data.get('note', '')
        # Cập nhật payment
        Payment.objects.filter(policy=policy).update(status="success")
        policy.activate()

        # Tạo thông báo trong hệ thống
        Notification.objects.create(
            user=policy.customer.user,
            message=f"Hợp đồng #{policy.id} đã được duyệt và có hiệu lực từ {policy.start_date:%d/%m/%Y} đến {policy.end_date:%d/%m/%Y}.",
            notification_type="policy_update",
        )
        messages.success(request, "Đã duyệt hợp đồng thành công!")
        # Gửi email cho khách hàng
        customer_email = policy.customer.user.email
        if customer_email:
            subject = "Hợp đồng bảo hiểm của bạn đã được duyệt"
            message = (
                f"Kính chào {policy.customer.user.get_full_name()},\n\n"
                f"Hợp đồng bảo hiểm #{policy.policy_number} của bạn đã được duyệt.\n"
                f"Hiệu lực: {policy.start_date:%d/%m/%Y} - {policy.end_date:%d/%m/%Y}\n\n"
                "Vui lòng đăng nhập để xem chi tiết.\n\n"
                "Trân trọng,\nĐội ngũ hỗ trợ Bảo hiểm"
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [customer_email])

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def api_reject_policy(request, pk):
    try:
        policy = get_object_or_404(Policy, pk=pk)
        data = json.loads(request.body)
        reason = data.get('reason', '').strip()

        if not reason:
            return JsonResponse({'success': False, 'error': 'Vui lòng nhập lý do'}, status=400)
        policy.cancel(True)

        Notification.objects.create(
            user=policy.customer.user,
            message=f"Hợp đồng #{policy.policy_number} đã bị từ chối. Lý do: {reason}",
            notification_type="policy_update",
        )
        messages.error(request, "Đã hủy tiếp nhận hợp đồng!")
        # Gửi email
        customer_email = policy.customer.user.email
        if customer_email:
            subject = "Hợp đồng bảo hiểm của bạn bị từ chối"
            message = (
                f"Kính chào {policy.customer.user.get_full_name()},\n\n"
                f"Hợp đồng bảo hiểm #{policy.policy_number} của bạn đã bị từ chối.\n"
                f"Lý do: {reason}\n\n"
                "Vui lòng liên hệ bộ phận hỗ trợ nếu có thắc mắc.\n\n"
                "Trân trọng,\nĐội ngũ hỗ trợ Bảo hiểm"
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [customer_email])

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



@login_required
def transfer_servicing_agent_api(request, pk):
    if not request.user.is_superuser:
        return JsonResponse({"success": False, "message": "Bạn không có quyền thực hiện thao tác này."}, status=403)

    try:
        data = json.loads(request.body)
        new_agent_id = data.get('new_agent_id')
        reason = data.get('reason', '')
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Dữ liệu yêu cầu không hợp lệ (JSON Error)."}, status=400)

    if not new_agent_id or not reason:
        return JsonResponse({"success": False, "message": "Vui lòng chọn đại lý mới và nhập lý do."}, status=400)

    policy = get_object_or_404(Policy, pk=pk)

    try:
        new_agent = Agent.objects.get(pk=new_agent_id)
    except Agent.DoesNotExist:
        return JsonResponse({"success": False, "message": "Đại lý mới không tồn tại."}, status=404)

    old_agent = policy.agent_servicing

    try:
        with transaction.atomic():

            # 2. Cập nhật Hợp đồng
            policy.agent_servicing = new_agent
            policy.save(update_fields=['agent_servicing', 'updated_at'])

            messages.success(request, "Đã chuyển đại lý quản lý thành công!")
            # 3. Kích hoạt thông báo (nếu cần)
            # notify_agent_transfer(policy, old_agent, new_agent)

    except Exception as e:

        return JsonResponse({"success": False, "message": f"Lỗi xử lý: {str(e)}"}, status=500)

    # Phản hồi thành công
    return JsonResponse({
        "success": True,
        "message": f"Chuyển đại lý quản lý thành công sang {new_agent.user.get_full_name()}.",
        "new_agent_name": new_agent.user.get_full_name(),
        "new_agent_id": new_agent.pk,
        "code_agent":new_agent.code,
    })