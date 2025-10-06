from datetime import timezone

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from policies.models import Policy
from django.db import models
from datetime import timedelta
from django.utils import timezone
@login_required
def custom_policies_admin(request):
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    product = request.GET.get('product', '')

    # Lấy tất cả hợp đồng + join với customer và product
    policies = Policy.objects.select_related('customer', 'product').all()

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

    context = {
        'policies': policies
    }
    return render(request, 'admin/policies_section.html', context)

@login_required
def dashboard_view_user(request):
    user = request.user

    # Tổng hợp đồng
    total_contracts = Policy.objects.filter(customer__user_id=user.id).count()

    # Đang hiệu lực
    active_contracts = Policy.objects.filter(customer__user=user, policy_status="active").count()

    # Phí hàng năm
    year_fee = Policy.objects.filter(customer__user=user).aggregate(total=models.Sum("premium_amount"))["total"] or 0
    year_fee_display = format_money(year_fee)
    # Tổng giá trị bảo hiểm
    total_insurance = Policy.objects.filter(customer__user=user).aggregate(total=models.Sum("sum_insured"))["total"] or 0
    total_insurance_display = format_money(total_insurance)

    search_query = request.GET.get("q","")
    policies = Policy.objects.select_related("product").filter(customer__user=user)
    if search_query:
        policies = policies.filter(
            Q(policy_number__icontains=search_query) |
            Q(product__product_name__icontains=search_query)
        )
    status = request.GET.get("status")
    if status:
        policies = policies.filter(policy_status=status)

    context = {
        "total_contracts": total_contracts,
        "active_contracts": active_contracts,
        "year_fee": year_fee_display,
         "total_insurance": total_insurance_display,
        "policies": policies,
        "search_query":search_query
    }
    return render(request, "users/policies_users.html", context)


def format_money(value):
    """Format số tiền: 2000000 -> 2M, 2100000 -> 2.1M"""
    value = float(value or 0)
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}".rstrip("0").rstrip(".") + "M"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}".rstrip("0").rstrip(".") + "K"
    return str(int(value))
@login_required
def policies_list_user(request):
    user = request.user
    policies = Policy.objects.select_related("product").filter(customer__user=user)
    return render(request, "policies_users.html", {"policies": policies})

def search_policies(user, search_query=""):
    """
    Lọc hợp đồng theo user + tìm kiếm theo mã hợp đồng hoặc tên sản phẩm.
    """
    policies = Policy.objects.select_related("product").filter(customer__user=user)

    if search_query:
        policies = policies.filter(
            Q(policy_number__icontains=search_query) |
            Q(product__product_name__icontains=search_query)
        )

    return policies
from django.shortcuts import render, redirect, get_object_or_404
from .models import Policy
from .forms import PolicyForm
from django.contrib import messages

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
def admin_policy_create(request):
    """Tạo hợp đồng"""
    if request.method == 'POST':
        form = PolicyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã thêm hợp đồng thành công!")
            return redirect('admin_policy_list')
    else:
        form = PolicyForm()
    return render(request, 'admin/policies_form.html', {'form': form, 'title': 'Tạo Hợp Đồng'})


@login_required
def admin_policy_detail(request, pk):
    """Xem chi tiết"""
    policy = get_object_or_404(Policy, pk=pk)
    return render(request, 'admin/policies_detail.html', {'policy': policy})


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

        policy.policy_status = "active"  # đặt lại trạng thái nếu cần
        policy.save()

        messages.success(request, f"Hợp đồng {policy.policy_number} đã được gia hạn thành công!")
        return redirect('admin_policy_list')

    return render(request, 'admin/policies_confirm_renew.html', {'old_policy': policy})


@login_required
def admin_policy_cancel(request, pk):
    """Hủy hợp đồng"""
    policy = get_object_or_404(Policy, pk=pk)
    if request.method == 'POST':
        policy.policy_status = "cancelled"
        policy.save()
        messages.warning(request, f"Hợp đồng {policy.policy_number} đã bị hủy.")
        return redirect('admin_policy_list')
    return render(request, 'admin/policies_confirm_cancel.html', {'policy': policy})
