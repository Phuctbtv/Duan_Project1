from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from policies.views import format_money
from .models import Claim
from django.contrib.auth.models import User
from django.db.models import Sum, Q

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
