from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re
User = get_user_model()

class ChangePasswordForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Mật khẩu mới",
        widget=forms.PasswordInput,
        strip=False
    )
    password2 = forms.CharField(
        label="Xác nhận mật khẩu mới",
        widget=forms.PasswordInput,
        strip=False
    )
    class Meta:
        model = User
        fields = []

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if not password:
            raise ValidationError("Vui lòng nhập mật khẩu.")
        if len(password) < 8:
            raise ValidationError("Mật khẩu phải có ít nhất 8 ký tự.")
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Mật khẩu phải có ít nhất 1 chữ hoa.")
        if not re.search(r"\d", password):
            raise ValidationError("Mật khẩu phải có ít nhất 1 số.")
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                raise ValidationError("Hai mật khẩu không khớp nhau.")
        return password2

    def save(self, commit=True, user=None):
        if not user:
            raise ValueError("Cần truyền user instance để đặt lại mật khẩu")

        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user