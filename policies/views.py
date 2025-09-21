from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from policies.models import Policy
from django.db import models

def custom_policies_admin(request):
    return render(request, 'admin/policies_section.html')

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