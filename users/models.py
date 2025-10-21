# The corrected User model
import os

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

from insurance_products.models import InsuranceProduct

class User(AbstractUser):
    """Model người dùng mở rộng từ AbstractUser"""

    USER_TYPES = [
        ("customer", "Khách hàng"),
        ("employee", "Nhân viên"),
        ("admin", "Quản trị viên"),
    ]

    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Số điện thoại phải đúng định dạng: '+999999999'. Tối đa 15 chữ số.",
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=20,
        blank=True,
        verbose_name="Số điện thoại",
    )

    address = models.TextField(blank=True, verbose_name="Địa chỉ")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")

    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPES,
        default="customer",
        verbose_name="Loại người dùng",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        db_table = "users"
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return f"{self.username}"

def upload_cccd_front(instance, filename):
    return f"ekyc/customer_{instance.user.id}/cccd_front{os.path.splitext(filename)[1]}"

def upload_cccd_back(instance, filename):
    return f"ekyc/customer_{instance.user.id}/cccd_back{os.path.splitext(filename)[1]}"

def upload_selfie(instance, filename):
    return f"ekyc/customer_{instance.user.id}/selfie{os.path.splitext(filename)[1]}"

def upload_health_certificate(instance, filename):
    return f"ekyc/customer_{instance.user.id}/health_certificate{os.path.splitext(filename)[1]}"

class Customer(models.Model):
    """Model khách hàng"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, verbose_name="Người dùng"
    )
    id_card_number = models.CharField(
        max_length=20, unique=True, verbose_name="Số CMND/CCCD"
    )
    nationality = models.CharField(
        max_length=50, default="Việt Nam", verbose_name="Quốc tịch"
    )
    cccd_front = models.FileField(upload_to=upload_cccd_front, null=True, blank=True)
    cccd_back = models.FileField(upload_to=upload_cccd_back, null=True, blank=True)
    selfie = models.FileField(upload_to=upload_selfie, null=True, blank=True)
    health_certificate = models.FileField(
        upload_to=upload_health_certificate, null=True, blank=True, verbose_name="Giấy khám sức khỏe"
    )
    GENDERS = [
        ("male", "Nam"),
        ("female", "Nữ"),
        ("other","Khác")
    ]

    gender = models.CharField(
        max_length=10, choices=GENDERS, default="other", verbose_name="Giới tính"
    )
    job = models.CharField(max_length=100, blank=True, verbose_name="Nghề nghiệp")
    class Meta:
        db_table = "customers"
        verbose_name = "Khách hàng"
        verbose_name_plural = "Khách hàng"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.id_card_number}"

class HealthInfo(models.Model):
    """Thông tin sức khỏe của khách hàng tại thời điểm mua bảo hiểm"""

    SMOKING_CHOICES = [
        ("never", "Không hút"),
        ("former", "Đã bỏ"),
        ("current", "Đang hút"),
    ]
    ALCOHOL_CHOICES = [
        ("no", "Không"),
        ("sometimes", "Thỉnh thoảng"),
    ]

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="health_records", verbose_name="Khách hàng"
    )

    height = models.PositiveIntegerField(verbose_name="Chiều cao (cm)")
    weight = models.PositiveIntegerField(verbose_name="Cân nặng (kg)")
    smoker = models.CharField(max_length=20, choices=SMOKING_CHOICES, verbose_name="Hút thuốc")
    alcohol = models.CharField(max_length=20, choices=ALCOHOL_CHOICES, verbose_name="Uống rượu/bia")
    conditions = models.JSONField(default=list, verbose_name="Tiền sử bệnh lý")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "health_info"
        verbose_name = "Thông tin sức khỏe"
        verbose_name_plural = "Thông tin sức khỏe"

    def __str__(self):
        return f"Sức khỏe {self.customer.user.username}"
