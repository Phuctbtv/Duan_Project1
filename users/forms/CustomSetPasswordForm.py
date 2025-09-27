from django import forms
from django.contrib.auth.forms import SetPasswordForm
import re

class CustomSetPasswordForm(SetPasswordForm):
    error_messages = {
        "password_mismatch": "Hai mật khẩu bạn nhập không khớp. Vui lòng thử lại.",
        "password_too_weak": (
            "Mật khẩu phải có ít nhất 8 ký tự, chứa ít nhất 1 chữ hoa, "
            "1 số và 1 ký tự đặc biệt."
        ),
    }

    def clean_new_password1(self):
        password1 = self.cleaned_data.get("new_password1")

        # Kiểm tra độ dài
        if len(password1) < 8:
            raise forms.ValidationError(self.error_messages["password_too_weak"])

        # Kiểm tra chữ hoa
        if not re.search(r"[A-Z]", password1):
            raise forms.ValidationError(self.error_messages["password_too_weak"])

        # Kiểm tra số
        if not re.search(r"[0-9]", password1):
            raise forms.ValidationError(self.error_messages["password_too_weak"])

        # Kiểm tra ký tự đặc biệt
        if not re.search(r"[@$!%*?&]", password1):
            raise forms.ValidationError(self.error_messages["password_too_weak"])

        return password1
