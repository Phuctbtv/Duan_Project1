from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from users.decorators import admin_required
from users.models import User

@admin_required
def admin_home(request):
    return render(request, "admin/dashboard_section.html")


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from users.models import User, Customer
from users.decorators import admin_required


@admin_required
def custom_section(request):
    """Quản lý khách hàng - Tìm kiếm, phân loại"""
    # Lấy tham số tìm kiếm và filter từ URL
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    print("=" * 50)
    print(f"DEBUG: URL = {request.build_absolute_uri()}")
    print(f"DEBUG: Search query = '{search_query}'")
    print(f"DEBUG: Status filter = '{status_filter}'")
    print(f"DEBUG: GET parameters = {dict(request.GET)}")

    # Query cơ bản - lấy tất cả users là customer
    users = User.objects.filter(user_type='customer')
    print(f"DEBUG: Total customers = {users.count()}")

    # Áp dụng tìm kiếm theo tên, email, username
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
        print(f"DEBUG: After search = {users.count()} users")

    # Áp dụng filter trạng thái
    if status_filter:
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'suspended':
            users = users.filter(is_active=False)
        print(f"DEBUG: After status filter = {users.count()} users")

    print("=" * 50)

    context = {
        'users': users,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'admin/custom_section.html', context)


@admin_required
def customer_create(request):
    """Tạo khách hàng mới"""
    if request.method == 'POST':
        try:
            # Tạo User trước
            user = User.objects.create_user(
                username=request.POST.get('username'),
                email=request.POST.get('email'),
                password=request.POST.get('password', '123456'),  # Password mặc định
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                phone_number=request.POST.get('phone_number'),
                address=request.POST.get('address'),
                date_of_birth=request.POST.get('date_of_birth'),
                user_type='customer'
            )

            # Tạo Customer
            customer = Customer.objects.create(
                user=user,
                id_card_number=request.POST.get('id_card_number'),
                nationality=request.POST.get('nationality', 'Việt Nam'),
                gender=request.POST.get('gender', 'other'),
                job=request.POST.get('job', '')
            )

            messages.success(request, f'Đã tạo khách hàng {user.get_full_name()} thành công!')
            return redirect('custom_section')

        except Exception as e:
            messages.error(request, f'Lỗi khi tạo khách hàng: {str(e)}')

    return render(request, 'admin/customer_create.html')


@admin_required
def customer_detail(request, user_id):
    """Chi tiết khách hàng"""
    user = get_object_or_404(User, pk=user_id, user_type='customer')

    # Lấy thông tin customer nếu có
    try:
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        customer = None

    # Lấy các hợp đồng của khách hàng
    from policies.models import Policy
    policies = Policy.objects.filter(customer__user=user) if customer else []

    context = {
        'user': user,
        'customer': customer,
        'policies': policies,
    }
    return render(request, 'admin/customer_detail.html', context)


@admin_required
def customer_edit(request, user_id):
    """Chỉnh sửa thông tin khách hàng"""
    user = get_object_or_404(User, pk=user_id, user_type='customer')

    try:
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        customer = None

    if request.method == 'POST':
        try:
            # Cập nhật User
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.phone_number = request.POST.get('phone_number')
            user.address = request.POST.get('address')
            user.date_of_birth = request.POST.get('date_of_birth')
            user.is_active = request.POST.get('is_active') == 'on'
            user.save()

            # Cập nhật Customer nếu tồn tại
            if customer:
                customer.id_card_number = request.POST.get('id_card_number')
                customer.nationality = request.POST.get('nationality')
                customer.gender = request.POST.get('gender')
                customer.job = request.POST.get('job')
                customer.save()

            messages.success(request, f'Đã cập nhật thông tin {user.get_full_name()} thành công!')
            return redirect('custom_section')

        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật: {str(e)}')

    context = {
        'user': user,
        'customer': customer,
    }
    return render(request, 'admin/customer_edit.html', context)


@admin_required
def customer_toggle_status(request, user_id):
    """Kích hoạt/Vô hiệu hóa khách hàng"""
    user = get_object_or_404(User, pk=user_id, user_type='customer')

    user.is_active = not user.is_active
    user.save()

    status = "kích hoạt" if user.is_active else "vô hiệu hóa"
    messages.success(request, f'Đã {status} khách hàng {user.get_full_name()}')

    return redirect('custom_section')


@admin_required
def customer_delete(request, user_id):
    """Xóa khách hàng"""
    user = get_object_or_404(User, pk=user_id, user_type='customer')

    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Đã xóa khách hàng {username} thành công!')
        return redirect('custom_section')

    return render(request, 'admin/customer_confirm_delete.html', {'user': user})