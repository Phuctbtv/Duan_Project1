from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from .models import Policy, PolicyHolder
from .forms import PolicyForm
from insurance_products.models import InsuranceProduct


@login_required
def custom_policies_admin(request):
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    product = request.GET.get('product', '')

    # Lấy tất cả sản phẩm từ CSDL để hiển thị dropdown
    products = InsuranceProduct.objects.all()

    # Lấy tất cả hợp đồng + join với customer và product
    policies = Policy.objects.select_related('customer', 'product').all()

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

    context = {
        'policies': policies,
        'products': products,
        'query': query,
        'status': status,
        'selected_product': product,
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
    year_fee = Policy.objects.filter(customer__user=user).aggregate(total=Sum("premium_amount"))["total"] or 0
    year_fee_display = format_money(year_fee)

    # Tổng giá trị bảo hiểm
    total_insurance = Policy.objects.filter(customer__user=user).aggregate(total=Sum("sum_insured"))["total"] or 0
    total_insurance_display = format_money(total_insurance)

    search_query = request.GET.get("q", "")
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
        "search_query": search_query
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
            # Validate ngày hiệu lực và ngày hết hạn
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            if start_date and end_date:
                if start_date >= end_date:
                    form.add_error('start_date', 'Ngày hiệu lực phải trước ngày hết hạn')
                    form.add_error('end_date', 'Ngày hết hạn phải sau ngày hiệu lực')
                    return render(request, 'admin/policies_form.html', {
                        'form': form,
                        'title': 'Tạo Hợp Đồng',
                        'action': 'create'
                    })

                # Kiểm tra ngày hiệu lực không được là quá khứ (tùy chọn)
                today = timezone.now().date()
                if start_date < today:
                    form.add_error('start_date', 'Ngày hiệu lực không được là ngày trong quá khứ')
                    return render(request, 'admin/policies_form.html', {
                        'form': form,
                        'title': 'Tạo Hợp Đồng',
                        'action': 'create'
                    })

            policy = form.save()
            messages.success(request, "Đã thêm hợp đồng thành công!")
            return redirect('policy_detail', pk=policy.pk)
    else:
        form = PolicyForm()

    context = {
        'form': form,
        'title': 'Tạo Hợp Đồng',
        'action': 'create'
    }
    return render(request, 'admin/policies_form.html', context)


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
        return render(request, 'users/components/policy/policies_detail.html', context)

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