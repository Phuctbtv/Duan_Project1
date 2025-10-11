# The corrected User model
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
class InsuranceProduct(models.Model):
    """Model sản phẩm bảo hiểm"""
    PRODUCT_TYPES = [
        ('auto','Bảo Hiểm Ô Tô'),
        ('health', 'Bảo Hiểm Sức Khỏe'),
        ('home', 'Bảo Hiểm Nhà Ở'),
        ('life', 'Bảo Hiểm Nhân Thọ'),
    ]

    name = models.CharField(max_length=100, verbose_name="Tên sản phẩm")
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, verbose_name="Loại bảo hiểm")
    description = models.TextField(verbose_name="Mô tả")
    base_rate = models.FloatField(verbose_name="Tỷ lệ phí cơ bản")
    is_active= models.BooleanField(default = True, verbose_name = "Đang hoạt động")

    class Meta:
        db_table = "insurance_products"
        verbose_name = "Sản phẩm bảo hiểm"
        verbose_name_plural = "Sản phẩm bảo hiểm"

    def __str__(self):
        return self.name

    class InsuranceContract(models.Model):
        """Model hợp đồng bảo hiểm"""
        STATUS_CHOICES =[
            ('draft', 'Nháp'),
            ('active', 'Đang hiệu lực'),
            ('expired', 'Đã hết hạn'),
        ]

        contract_number = models.CharField(max_length = 20, verbose_name="Số hợp đồng")
        customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Khách hàng")
        product = models.ForeignKey(InsuranceProduct, on_delete=models.CASCADE, verbose_name="Sản phẩm")
        insurance_amount =  models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Số tiền bảo hiểm")
        total_premium = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Tổng phí")
        status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Trạng thái")
        created_at = models.DateTimeField(auto_now_add=True)

        class Meta:
            db_table = "insurance_contracts"
            verbose_name = "Hợp đồng bảo hiểm"
            verbose_name_plural = "Hợp đồng bảo hiểm"

        def __str__(self):
            return f"{self.contract_number} - {self.customer.user.get_full_name()}"