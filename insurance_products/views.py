
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import InsuranceProduct
from django.core.paginator import Paginator
from django.http import JsonResponse
from policies.views import format_money
def custom_products_admin(request):
    return render(request, 'admin/products_section.html')
def insurance_products_user(request):
    # Lọc sản phẩm
    products = InsuranceProduct.objects.filter(is_active=True)
    # Lọc theo giá
    price_filter = request.GET.get('price', '')
    if price_filter:
        if '-' in price_filter:
            min_price, max_price = price_filter.split('-')
            products = products.filter(
                premium_base_amount__gte=int(min_price),
                premium_base_amount__lte=int(max_price)
            )
        elif price_filter.endswith('+'):
            min_price = int(price_filter.replace('+', ''))
            products = products.filter(premium_base_amount__gte=min_price)
    category = request.GET.get("category")
    if category:
        products = products.filter(product_type=category)
    # --- Age Filter ---
    age_filter = request.GET.get('age', '')
    if age_filter:
        if '-' in age_filter:
            min_age, max_age = age_filter.split('-')
            products = products.filter(
                eligible_min_age__gte=int(min_age),
                eligible_max_age__lte=int(max_age)
            )
        elif age_filter.endswith('+'):
            min_age = int(age_filter.replace('+', ''))
            products = products.filter(eligible_max_age__gte=min_age)
    # --- Coverage Filter ---
    coverage_filter = request.GET.get('coverage', '')
    if coverage_filter:
        if '-' in coverage_filter:
            min_cov, max_cov = coverage_filter.split('-')
            products = products.filter(
                max_claim_amount__gte=int(min_cov),
                max_claim_amount__lte=int(max_cov)
            )
        elif coverage_filter.endswith('+'):
            min_cov = int(coverage_filter.replace('+', ''))
            products = products.filter(max_claim_amount__gte=min_cov)
    # Tìm kiếm
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(coverage_details__icontains=search_query)
        )

    # Sắp xếp
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_asc':
        products = products.order_by('premium_base_amount')
    elif sort_by == 'price_desc':
        products = products.order_by('-premium_base_amount')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('product_name')

    # Phân trang
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'product_count': products.count(),
        'search_query': search_query,
        'selected_price': price_filter,
        'sort_by': sort_by,
        "category_choices": InsuranceProduct.PACKAGE_CHOICES,
    }

    return render(request, 'products/home_product_user.html',context)

def product_detail(request, product_id):
    product = get_object_or_404(InsuranceProduct, id=product_id, is_active=True)
    related_products = InsuranceProduct.objects.filter(
        product_type=product.product_type,
        is_active=True
    ).exclude(id=product_id)[:4]

    context = {
        'product': product,
        'related_products': related_products
    }
    return render(request, 'products/components/product_detail.html', context)



