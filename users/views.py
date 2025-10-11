from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AuthenticationForm

from users.decorators import user_required
from users.forms.RegisterForm import RegisterForm
from users.forms.ChangePasswordForm import ChangePasswordForm
from users.models import User, Customer

from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
# from .models import InsuranceProduct, InsuranceContract

from django.contrib.auth.views import PasswordResetConfirmView
from .forms.CustomSetPasswordForm import CustomSetPasswordForm
def trangchu(request):
    return render(request, "base/trangchu_base.html")
@login_required
def user_info_api(request):
    user = request.user
    customer = Customer.objects.get(user=user)

    data = {
        "full_name": f"{user.first_name} {user.last_name}".strip(),
        "email": user.email,
        "phone": user.phone_number,
        "birth_date":user.date_of_birth,
        "gender": customer.gender,
        "address": user.address,
        "id_card_number": customer.id_card_number,
        "occupation": customer.job,
        "cccd":customer.id_card_number,
        "nationality": customer.nationality,
    }

    return JsonResponse(data)

@csrf_protect
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=user.username, password=raw_password)

            if user is not None:
                login(request, user)
                messages.success(
                    request,
                    f"Tài khoản {user.get_username()} đã được tạo thành công! Chào mừng bạn đến với hệ thống!"
                )
                return redirect("trangchu")
        else:
            # Hiển thị lỗi cụ thể từ form
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


@csrf_protect
@csrf_protect
def login_view(request):
    #
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("admin_home")
        else:
            return redirect("trangchu")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(
                    request,
                    f"Xin chào {user.get_username()}, bạn đã đăng nhập thành công!"
                )

                # Sau khi đăng nhập xong phân quyền
                if user.is_staff:
                    return redirect("admin_home")
                else:
                    return redirect("trangchu")
            else:
                messages.error(request, "Tên đăng nhập hoặc mật khẩu không chính xác.")
        else:
            messages.error(request, "Vui lòng kiểm tra lại thông tin đăng nhập.")
    else:
        form = AuthenticationForm()

    return render(request, "users/login.html", {"form": form})

@user_required
def custom_users_user(request):
    return render(request, "users/quanlytaikhoan.html")
def custom_users_admin(request):
    users = User.objects.all()
    return render(request, "admin/custom_section.html", {"users": users})
def custom_contact_admin( request):
    return render(request, "admin/contact_section.html")

def profile_view(request):
    tab = request.GET.get("tab")
    if tab:
        request.session["active_tab"] = tab
    else:
        tab = request.session.get("active_tab", "profile_info")

    context = {
        "active_tab": tab
    }
    return render(request, "users/profile_user.html", context)

@login_required
def update_profile(request):
    if request.method == "POST":
        user = request.user
        # Cập nhật thông tin user
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.phone_number = request.POST.get("phone_number")
        user.address = request.POST.get("address")
        user.date_of_birth = request.POST.get("date_of_birth")
        user.save()

        # Cập nhật hoặc tạo Customer
        customer, created = Customer.objects.get_or_create(user=user)
        customer.gender = request.POST.get("gender")
        customer.id_card_number = request.POST.get("id_card_number")
        customer.job = request.POST.get("job")
        customer.save()
        messages.success(request, " Cập nhật thông tin thành công!")
        return redirect("custom_profile_user")

    return redirect("custom_profile_user")

@login_required(login_url="login")
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        current_password = request.POST.get('current_password')

        if not request.user.check_password(current_password):
            messages.error(request, 'Mật khẩu hiện tại không đúng.')
            return render(
                request,
                'users/profile_user.html',
                {'formChangePassword': form, 'active_tab': 'security'}
            )

        if form.is_valid():
            new_password = form.cleaned_data['password1']

            if request.user.check_password(new_password):
                messages.error(request, "Mật khẩu mới không được trùng với mật khẩu hiện tại.")
                return render(
                    request,
                    "users/profile_user.html",
                    {"formChangePassword": form, "active_tab": "security"}
                )
            request.user.set_password(new_password)
            request.user.save()

            update_session_auth_hash(request, request.user)
            messages.success(request, 'Đổi mật khẩu thành công!')
            return redirect("custom_profile_user")
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.')
            return render(
                request,
                'users/profile_user.html',
                {'formChangePassword': form, 'active_tab': 'security'}
            )
    else:
        form = ChangePasswordForm()

    return redirect("custom_profile_user")


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'users/components/registration/password_reset_confirm.html'
    success_url = '/login/'


@login_required
def admin_home(request):
    """Dashboard cho admin"""
    if not request.user.is_staff:
        return redirect('trangchu')

    # DÙNG DỮ LIỆU TĨNH
    context = {
        'total_customers': 1234,
        'active_contracts': 856,
        'monthly_revenue': 58.5,
        'recent_claims': 42,
        'approval_rate': 94.2,
        'avg_processing_time': 2.3,
        'customer_satisfaction': 4.8,
    }

    return render(request, "admin/admin_home.html", context)
# @login_required
# def admin_home(request):
#     """Dashboard cho admin"""
#     if not request.user.is_staff:
#         return redirect("trangchu")
#
#     #lay thong ke tu database
#     total_customers = Customer.objects.count()
#     active_contracts = InsuranceContract.objects.filter(status='active').count()
#
#     #doanh thu thang hien tai
#     current_month = timezone.now().month
#     current_year = timezone.now().year
#
#     monthly_revenue = InsuranceContract.objects.filter(
#         created_at__month=current_month,
#         created_at__year=current_year,
#         status='active'
#     ).aggregate(total=Sum('total_premium'))['total'] or 0
#
#     #chuyen doi sang ty
#     monthly_revenue_billion = float(monthly_revenue) / 1000000000 if monthly_revenue else 0
#
#     #hoat dong gan day (5 hop dong moi nhat)
#     recent_activities = InsuranceContract.objects.select_related(
#         'customer', 'product', 'customer__user'
#     ).order_by('-created_at')[:5]
#
#     #du lieu cho bieu do
#     monthly_data = get_monthly_revenue_data()
#     contract_type_data = get_contract_type_data()
#
#     context = {
#         'total_customers': total_customers,
#         'active_contracts': active_contracts,
#         'monthly_revenue': round(monthly_revenue_billion, 1),
#         'recent_activities': recent_activities,
#
#         #du lieu bieu do
#         'monthly_labels': monthly_data['labels'],
#         'monthly_revenue': monthly_data['revenue'],
#         'contract_types': contract_type_data['types'],
#         'contract_counts': contract_type_data['counts'],
#     }
#
#     return render(request, "users/admin_home.html", context)
#
#
# def get_monthly_revenue_data():
#     """Lấy dữ liệu doanh thu 6 tháng gần nhất"""
#     months = []
#     revenues = []
#
#     for i in range(5, -1, -1):
#         date = timezone.now() - timedelta(days=30 * i)
#         month_year = date.strftime('%m/%Y')
#         months.append(month_year)
#
#         revenue = InsuranceContract.objects.filter(
#             created_at__month=date.month,
#             created_at__year=date.year,
#             status='active'
#         ).aggregate(total=Sum('total_premium'))['total'] or 0
#
#         revenues.append(float(revenue) / 1000000)  # Chuyển sang triệu VND
#
#     return {'labels': months, 'revenues': revenues}
#
#
# def get_contract_type_data():
#     """Lấy dữ liệu phân loại hợp đồng theo sản phẩm"""
#     contracts_by_type = InsuranceContract.objects.filter(
#         status='active'
#     ).values('product__product_type').annotate(
#         count=Count('id')
#     )
#
#     types = []
#     counts = []
#
#     type_names = {
#         'auto': 'Ô Tô',
#         'health': 'Sức Khỏe',
#         'home': 'Nhà Ở',
#         'life': 'Nhân Thọ'
#     }
#
#     for item in contracts_by_type:
#         type_key = item['product__product_type']
#         types.append(type_names.get(type_key, type_key))
#         counts.append(item['count'])
#
#     return {'types': types, 'counts': counts}
#
#
# # API cho biểu đồ
# @login_required
# def dashboard_chart_data(request):
#     """API cung cấp dữ liệu cho biểu đồ"""
#     if not request.user.is_staff:
#         return JsonResponse({'error': 'Unauthorized'}, status=403)
#
#     chart_type = request.GET.get('type', 'revenue')
#
#     if chart_type == 'revenue':
#         data = get_monthly_revenue_data()
#     elif chart_type == 'contracts':
#         data = get_contract_type_data()
#     else:
#         data = {}
#
#     return JsonResponse(data)