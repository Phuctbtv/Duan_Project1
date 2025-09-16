from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AuthenticationForm

from users.decorators import user_required
from users.forms.RegisterForm import RegisterForm
from users.models import User, Customer


def trangchu(request):
    return render(request, "base/trangchu_base.html")


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
    tab = request.GET.get("tab", "profile_info")
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

        return redirect("custom_profile_user")

    return redirect("custom_profile_user")


