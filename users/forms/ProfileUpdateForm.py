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
    cccd_front = forms.ImageField(
        label="Ảnh CCCD mặt trước",
        required=False,
    )

    cccd_back = forms.ImageField(
        label="Ảnh CCCD mặt sau",
        required=False,
    )

    ocr_verified = forms.BooleanField(
        label="Trạng thái xác thực OCR",
        required=False,
        widget=forms.CheckboxInput(attrs={'disabled': 'disabled'})
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

    def __init__(self, *args, **kwargs):
        """
        Hàm này tùy chỉnh form dựa trên trạng thái của user
        """
        user = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if user:
            customer = getattr(user, 'customer', None)
            if customer and not customer.ocr_verified:
                # Bắt buộc người dùng phải tải lên ảnh
                self.fields['cccd_front'].required = True
                self.fields['cccd_back'].required = True

                self.fields['cccd_front'].help_text = "Bạn phải tải lên ảnh để xác thực eKYC."
                self.fields['cccd_back'].help_text = "Bạn phải tải lên ảnh để xác thực eKYC."
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

    def clean(self):
        cleaned_data = super().clean()
        front_image = cleaned_data.get("cccd_front")
        back_image = cleaned_data.get("cccd_back")

        if (front_image and not back_image) or (not front_image and back_image):
            raise forms.ValidationError(
                "Bạn phải tải lên CẢ MẶT TRƯỚC VÀ MẶT SAU của CCCD trong cùng một lần."
            )

        return cleaned_data

        return cleaned_data
    def save(self, commit=True):
        user = super().save(commit=False)
        customer, _ = Customer.objects.get_or_create(user=user)

        # Cập nhật các trường thông thường
        customer.gender = self.cleaned_data.get("gender")
        customer.id_card_number = self.cleaned_data.get("id_card_number")
        customer.job = self.cleaned_data.get("job")

        front_image = self.cleaned_data.get("cccd_front")
        back_image = self.cleaned_data.get("cccd_back")

        new_front_uploaded = False
        new_back_uploaded = False

        if front_image:
            if customer.cccd_front:
                customer.cccd_front.delete(save=False)
            customer.cccd_front = front_image
            new_front_uploaded = True
        if back_image:
            if customer.cccd_back:
                customer.cccd_back.delete(save=False)
            customer.cccd_back = back_image
            new_back_uploaded = True

        if new_front_uploaded and new_back_uploaded:
            customer.ocr_verified = True
        if commit:
            user.save()
            customer.save()

        return user