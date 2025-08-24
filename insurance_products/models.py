from django.db import models


class InsuranceProduct(models.Model):
    """Model sản phẩm bảo hiểm"""

    CURRENCY_CHOICES = [
        ("VND", "Việt Nam Đồng"),
        ("USD", "US Dollar"),
    ]

    product_name = models.CharField(
        max_length=100, unique=True, verbose_name="Tên sản phẩm"
    )
    description = models.TextField(verbose_name="Mô tả")
    coverage_details = models.TextField(verbose_name="Chi tiết bảo hiểm")
    terms_and_conditions = models.TextField(verbose_name="Điều khoản và điều kiện")
    premium_base_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Phí bảo hiểm cơ bản"
    )
    currency = models.CharField(
        max_length=5,
        choices=CURRENCY_CHOICES,
        default="VND",
        verbose_name="Đơn vị tiền tệ",
    )
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        db_table = "insurance_product"
        verbose_name = "Sản phẩm bảo hiểm"
        verbose_name_plural = "Sản phẩm bảo hiểm"

    def __str__(self):
        return self.product_name
