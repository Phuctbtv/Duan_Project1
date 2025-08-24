from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "input-focus w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent",
                "placeholder": "Tên_người_dùng",
            }
        ),
        label="Tên đăng nhập",
        help_text="Chỉ được chứa chữ cái, số và ký tự @/./+/-/_"
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "class": "input-focus w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent",
                "placeholder": "Văn A",
            }
        ),
        label="Tên",
    )

    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "class": "input-focus w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent",
                "placeholder": "Nguyễn",
            }
        ),
        label="Họ",
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "input-focus w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent",
                "placeholder": "example@email.com",
            }
        ),
        label="Email",
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "input-focus w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent",
                "placeholder": "0325349348",
            }
        ),
        label="Phone Number",
    )

    date_of_birth = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "input-focus w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent",
            }
        ),
        label="Ngày sinh",
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "input-focus w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent",
                "placeholder": "Tối thiểu 8 ký tự",
                "id": "registerPassword",
            }
        ),
        label="Mật khẩu",
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "input-focus w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent",
                "placeholder": "Nhập lại mật khẩu",
                "id": "confirmPassword",
            }
        ),
        label="Xác nhận mật khẩu",
    )

    terms_accepted = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={
                "class": "h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
            }
        ),
        label="Tôi đồng ý với Điều khoản dịch vụ và Chính sách bảo mật",
        required=True,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "password1",
            "password2",
        )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        # Kiểm tra độ dài tối thiểu
        if len(username) < 3:
            raise ValidationError("Tên đăng nhập phải có ít nhất 3 ký tự.")

        # Kiểm tra ký tự hợp lệ (chỉ chữ cái, số và một số ký tự đặc biệt)
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError("Tên đăng nhập chỉ được chứa chữ cái, số và ký tự @/./+/-/_")

        # Kiểm tra username đã tồn tại
        if User.objects.filter(username=username).exists():
            raise ValidationError("Tên đăng nhập này đã được sử dụng.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email này đã được sử dụng.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        if not re.match(r"^\d{10,11}$", phone):
            raise ValidationError("Số điện thoại phải có 10-11 chữ số.")
        return phone

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if len(password) < 8:
            raise ValidationError("Mật khẩu phải có ít nhất 8 ký tự.")
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Mật khẩu phải có ít nhất 1 chữ hoa.")
        if not re.search(r"\d", password):
            raise ValidationError("Mật khẩu phải có ít nhất 1 số.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.date_of_birth = self.cleaned_data["date_of_birth"]
        user.set_password(self.cleaned_data["password1"])
        user.phone_number = self.cleaned_data["phone_number"]

        if commit:
            user.save()
        return user
