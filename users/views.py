import base64
import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.forms import AuthenticationForm

from users.decorators import user_required
from users.forms.RegisterForm import RegisterForm
from users.forms.ChangePasswordForm import ChangePasswordForm
from users.models import User, Customer

import requests

from django.http import JsonResponse

from django.contrib.auth.views import PasswordResetConfirmView

from .forms.ProfileUpdateForm import ProfileUpdateForm
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
def login_view(request):
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
                #  Kiểm tra nếu tài khoản bị khóa
                if not user.is_active:
                    messages.error(request, "Tài khoản của bạn đang bị tạm khóa. Vui lòng liên hệ quản trị viên.")
                    return redirect("login")

                # Đăng nhập thành công
                login(request, user)
                list(messages.get_messages(request))
                messages.success(
                    request,
                    f"Xin chào {user.get_username()}, bạn đã đăng nhập thành công!"
                )
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
    user = request.user
    customer = getattr(user, 'customer', None)

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save()
            customer = user.customer

            if customer.ocr_verified:
                messages.success(request, "Cập nhật thông tin và xác thực eKYC thành công!")

            else:
                front_image = form.cleaned_data.get("cccd_front")
                back_image = form.cleaned_data.get("cccd_back")

                if front_image or back_image:
                    # Người dùng CÓ tải ảnh lên, nhưng KHÔNG ĐỦ 2 CÁI
                    messages.warning(request,
                                     "Cập nhật thành công! Tuy nhiên, bạn phải tải lên CẢ MẶT TRƯỚC VÀ MẶT SAU của CCCD "
                                     "trong cùng một lần để hoàn tất xác thực eKYC."
                                     )
                else:
                    messages.success(request, "Cập nhật thông tin thành công!")

            return redirect("custom_profile_user")
        else:
            all_errors = []
            for field, errors in form.errors.items():
                for error in errors:
                    all_errors.append(error)


            error_text = " ".join(all_errors)
            messages.error(request, f"LỖI : {error_text}")
            return render(
                request,
                'users/profile_user.html',
                {'form': form, 'active_tab': 'profile_info'}
            )

    else:
        initial_data = {}
        if customer:
            initial_data = {
                "gender": customer.gender,
                "id_card_number": customer.id_card_number,
                "job": customer.job,
            }
        form = ProfileUpdateForm(instance=user, initial=initial_data)

    return render(
        request,
        'users/profile_user.html',
        {'form': form, 'active_tab': 'profile_info'}
    )
@csrf_exempt
def ocr_cccd(request):
    """
    Trích xuất thông tin từ ảnh CCCD (phiên bản cải tiến)
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"})

    image_file = request.FILES.get("image")
    if not image_file:
        return JsonResponse({"success": False, "error": "No image uploaded"})


    image_type = image_file.content_type
    allowed_types = ["image/jpeg", "image/png", "image/webp"]

    if image_type not in allowed_types:
        return JsonResponse({
            "success": False,
            "error": f"Invalid image type: {image_type}. Only JPEG, PNG, or WebP are allowed."
        })
    # ------------------------------------

    image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
    GEMINI_API_KEY = settings.GEMINI_API_KEY

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "Trích xuất thông tin từ ảnh CCCD và trả về DẠNG JSON thuần. "
                            "Quan trọng: Tên phải được xử lý theo quy tắc của người Việt Nam. "
                            "Sử dụng các trường sau: "
                            "'ho_va_ten_dem' (Ví dụ: Nguyễn Văn), "
                            "'ten' (Ví dụ: A), "
                            "'id_number' (Số CCCD), "
                            "'gioi_tinh' (Giới tính, chỉ trả về một trong ba giá trị: 'male', 'female', hoặc 'other'. 'male' cho Nam, 'female' cho Nữ), "
                            "'date_of_birth' (Ngày sinh, định dạng YYYY-MM-DD), "
                            "'address' (Địa chỉ thường trú). "
                            "Chỉ trả JSON, không thêm mô tả hoặc văn bản khác."
                        )
                    },
                    {
                        "inline_data": {
                            "mime_type": image_type,
                            "data": image_base64
                        }
                    }
                ]
            }
        ]
    }

    try:
        res = requests.post(url, json=payload, timeout=30)
        data = res.json()

        if "candidates" not in data:
            print("❌ Gemini API Error:", data)
            return JsonResponse({
                "success": False,
                "error": data.get("error", {}).get("message", "Invalid Gemini response"),
                "raw_response": data
            })

        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()

        # Thêm một bước kiểm tra JSON trước khi parse
        if not text.startswith("{") or not text.endswith("}"):
            raise ValueError("Model did not return valid JSON.")

        result = json.loads(text)

        return JsonResponse({
            "success": True,
            "data": {
                "first_name": result.get("ho_va_ten_dem"),
                "last_name": result.get("ten"),
                "id_number": result.get("id_number"),
                "gender":result.get("gioi_tinh"),
                "date_of_birth": result.get("date_of_birth"),
                "address": result.get("address")
            }
        })

    # Bắt lỗi cụ thể hơn
    except json.JSONDecodeError:
        print("❌ JSON Decode Error. Model response:", text)
        return JsonResponse({"success": False, "error": "Failed to parse OCR data. Model returned non-JSON."})
    except requests.exceptions.Timeout:
        return JsonResponse({"success": False, "error": "Request timed out. The server is busy."})
    except Exception as e:
        print("❌ OCR Exception:", str(e))
        return JsonResponse({"success": False, "error": str(e)})

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


