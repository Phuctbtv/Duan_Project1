
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import InsuranceProductForm
from .models import InsuranceProduct
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import JsonResponse

@login_required
def custom_products_admin(request):
    products_qs = InsuranceProduct.objects.all().order_by('-id')

    # Lọc tên
    q = request.GET.get('q', '')
    if q:
        products_qs = products_qs.filter(product_name__icontains=q)

    # Lọc loại sản phẩm
    product_type = request.GET.get('product_type', '')
    if product_type:
        products_qs = products_qs.filter(product_type=product_type)

    # Phân trang bình thường (tuỳ chọn)
    paginator = Paginator(products_qs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'products': page_obj}

    # Nếu là AJAX, trả về partial HTML
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('admin/products_list_partial.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, 'admin/products_section.html', context)



def add_product_view(request):
    if request.method == 'POST':
        form = InsuranceProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.is_active = True  # tự động Active
            product.created_at = timezone.now()
            product.updated_at = timezone.now()
            product.save()
            return redirect('custom_products_admin')  # quay lại danh sách
    else:
        form = InsuranceProductForm()

    return render(request, 'admin/add_product.html', {'form': form})
def edit_product_view(request, product_id):
    product = get_object_or_404(InsuranceProduct, id=product_id)

    if request.method == 'POST':
        form = InsuranceProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            # ép kiểu bool
            product.is_active = request.POST.get('is_active') == 'True'
            product.save()
            return redirect('custom_products_admin')  # quay lại trang danh sách sản phẩm
    else:
        form = InsuranceProductForm(instance=product)

    return render(request, 'admin/edit_product.html', {'form': form, 'product': product})


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

    recent_products = request.session.get("recent_products", [])
    if product_id in recent_products:
        recent_products.remove(product_id)
    recent_products.insert(0, product_id)
    request.session["recent_products"] = recent_products[:3]

    context = {
        'product': product,
        'related_products': related_products
    }
    return render(request, 'products/components/product_detail.html', context)
def recent_products(request, product_id):
    product = get_object_or_404(InsuranceProduct, id=product_id)

    # --- Lưu sản phẩm vào session ---
    recent_products = request.session.get("recent_products", [])

    # Nếu sản phẩm đã có thì xóa (tránh trùng lặp)
    if product.id in recent_products:
        recent_products.remove(product.id)

    # Thêm sản phẩm mới vào đầu danh sách
    recent_products.insert(0, product.id)

    # Chỉ giữ tối đa 3 sản phẩm
    recent_products = recent_products[:3]

    # Cập nhật lại session
    request.session["recent_products"] = recent_products

    return redirect("payments_users")



