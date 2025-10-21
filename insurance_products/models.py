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
        max_digits=12, decimal_places=2, verbose_name="Phí bảo hiểm cơ bản"
    )
    currency = models.CharField(
        max_length=5,
        choices=CURRENCY_CHOICES,
        default="VND",
        verbose_name="Đơn vị tiền tệ",
    )
    max_claim_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Mức chi trả tối đa",
    )
    PACKAGE_CHOICES = [
        ('basic', 'Gói Cơ bản'),
        ('standard', 'Gói Tiêu chuẩn'),
        ('premium', 'Gói Cao cấp'),
    ]

    product_type = models.CharField(
        max_length=20,
        choices=PACKAGE_CHOICES,
        default='standard',
        verbose_name="Loại gói bảo hiểm"
    )

    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        db_table = "insurance_product"
        verbose_name = "Sản phẩm bảo hiểm"
        verbose_name_plural = "Sản phẩm bảo hiểm"
    def format_money(self, value):
        """Format số tiền: 2000000 -> 2M, 2100000 -> 2.1M"""
        value = float(value or 0)
        if value >= 1_000_000:
            return f"{value/1_000_000:.1f}".rstrip("0").rstrip(".") + "M"
        elif value >= 1_000:
            return f"{value/1_000:.1f}".rstrip("0").rstrip(".") + "K"
        return str(int(value))

    def premium_base_amount_short(self):
        return self.format_money(self.premium_base_amount)
    def max_claim_amount_short(self):
        return self.format_money(self.max_claim_amount)
    def __str__(self):
        return self.product_name
