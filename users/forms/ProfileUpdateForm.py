from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re
from datetime import  date

from users.models import Customer

User = get_user_model()

class ProfileUpdateForm(forms.ModelForm):

    gender = forms.ChoiceField(
        choices=[("male", "Nam"), ("female", "Nữ")],
        label="Giới tính",
        required=False,
    )
    id_card_number = forms.CharField(
        max_length=12,
        label="CMND/CCCD",
        required=True,
    )
    job = forms.CharField(
        max_length=100,
        label="Nghề nghiệp",
        required=False,
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "date_of_birth",
            "address",
            "phone_number",
            "email",
        ]
        labels = {
            "first_name": "Họ",
            "last_name": "Tên",
            "date_of_birth": "Ngày sinh",
            "address": "Địa chỉ",
            "phone_number": "Số điện thoại",
            "email": "Email",
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        if not re.match(r"^\d{10,11}$", phone):
            raise ValidationError("Số điện thoại phải có 10-11 chữ số.")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get("email")
        user = self.instance
        if User.objects.filter(email=email).exclude(pk=user.pk).exists():
            raise ValidationError("Email này đã được sử dụng.")
        return email

    def clean_id_card_number(self):
        id_card = self.cleaned_data.get("id_card_number")
        user = self.instance

        # Kiểm tra định dạng
        if not re.match(r"^\d{9,12}$", id_card):
            raise ValidationError("CMND/CCCD phải có từ 9 đến 12 chữ số.")

        if Customer.objects.filter(id_card_number=id_card).exclude(user=user).exists():
            raise ValidationError("Số CMND/CCCD này đã được sử dụng.")

        return id_card

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get("date_of_birth")
        today = date.today()
        if not dob:
            raise ValidationError("Vui lòng nhập ngày sinh.")
        if dob > today:
            raise ValidationError("Ngày sinh không hợp lệ.")
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18:
            raise ValidationError("Bạn phải đủ 18 tuổi để cập nhật thông tin.")
        return dob



    def save(self, commit=True):
        user = super().save(commit=False)
        customer, _ = Customer.objects.get_or_create(user=user)

        customer.gender = self.cleaned_data.get("gender")
        customer.id_card_number = self.cleaned_data.get("id_card_number")
        customer.job = self.cleaned_data.get("job")

        if commit:
            user.save()
            customer.save()

        return user