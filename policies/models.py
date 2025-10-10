from datetime import timedelta

from django.db import models
from users.models import Customer
from insurance_products.models import InsuranceProduct
from django.utils import timezone

class Policy(models.Model):
    """Model hợp đồng bảo hiểm"""

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Chờ thanh toán"),
        ("paid", "Đã thanh toán"),
        ("overdue", "Quá hạn"),
        ("cancelled", "Đã hủy"),
    ]

    POLICY_STATUS_CHOICES = [
        ("active", "Đang hoạt động"),
        ("expired", "Đã hết hạn"),
        ("cancelled", "Đã hủy"),
        ("pending", "Chờ xử lý"),
    ]

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, verbose_name="Khách hàng"
    )
    product = models.ForeignKey(
        InsuranceProduct, on_delete=models.CASCADE, verbose_name="Sản phẩm bảo hiểm"
    )
    policy_number = models.CharField(
        max_length=50, unique=True, verbose_name="Số hợp đồng"
    )
    start_date = models.DateField(verbose_name="Ngày hiệu lực",null=True)
    end_date = models.DateField(verbose_name="Ngày hết hạn",null=True)
    premium_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Phí bảo hiểm"
    )
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
        verbose_name="Trạng thái thanh toán",
    )
    policy_status = models.CharField(
        max_length=10,
        choices=POLICY_STATUS_CHOICES,
        default="pending",
        verbose_name="Trạng thái hợp đồng",
    )
    policy_document_url = models.URLField(
        blank=True, verbose_name="URL tài liệu hợp đồng"
    )
    sum_insured = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Tổng số tiền bảo hiểm",

    )
    claimed_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Tổng số tiền đã chi trả",
        null=True, blank=True

    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        db_table = "policies"
        verbose_name = "Hợp đồng bảo hiểm"
        verbose_name_plural = "Hợp đồng bảo hiểm"

    def remaining_days(self):
        if not self.end_date:
            return "Chưa kích hoạt"
        days = (self.end_date - timezone.now().date()).days
        return days

    def progress_percent(self):
        if not self.start_date or not self.end_date:
            return 0

        total_days = (self.end_date - self.start_date).days
        used_days = (timezone.now().date() - self.start_date).days

        if total_days <= 0:
            return 0

        progress = round((used_days / total_days) * 100)
        return min(max(progress, 0), 100)

    def format_money(self, value):
        """Format số tiền: 2000000 -> 2M, 2100000 -> 2.1M"""
        value = float(value or 0)
        if value >= 1_000_000:
            return f"{value/1_000_000:.1f}".rstrip("0").rstrip(".") + "M"
        elif value >= 1_000:
            return f"{value/1_000:.1f}".rstrip("0").rstrip(".") + "K"
        return str(int(value))

    def premium_short(self):
        return self.format_money(self.premium_amount)

    def sum_insured_short(self):
        return self.format_money(self.sum_insured)

    def activate(self):
        """Kích hoạt hợp đồng sau khi thanh toán thành công"""
        self.payment_status = "paid"
        self.policy_status = "active"
        self.start_date = timezone.now().date()
        self.end_date = self.start_date + timedelta(days=365)  # giả định 1 năm
        self.save()

    def cancel(self):
        """Hủy hợp đồng nếu thanh toán thất bại hoặc khách hủy"""
        self.payment_status = "cancelled"
        self.policy_status = "cancelled"
        self.save()
    def __str__(self):
        return f"{self.policy_number} - {self.customer.user.username}"


class PolicyHolder(models.Model):
    """Model người được bảo hiểm"""

    RELATIONSHIP_CHOICES = [
        ('spouse', 'Vợ/Chồng'),
        ('child', 'Con'),
        ('parent', 'Cha/Mẹ'),
        ('sibling', 'Anh/Chị/Em'),
        ('me', 'Chính mình'),
    ]

    policy = models.ForeignKey(
        Policy, on_delete=models.CASCADE, verbose_name="Hợp đồng bảo hiểm"
    )
    full_name = models.CharField(max_length=100, verbose_name="Họ và tên")
    date_of_birth = models.DateField(verbose_name="Ngày sinh")
    id_card_number = models.CharField(max_length=20, verbose_name="Số CMND/CCCD",null=True, blank=True)
    relationship_to_customer = models.CharField(
        max_length=50,
        choices=RELATIONSHIP_CHOICES,
        verbose_name="Mối quan hệ với khách hàng"
    )

    class Meta:
        db_table = "policyholders"
        verbose_name = "Người được bảo hiểm"
        verbose_name_plural = "Người được bảo hiểm"

    def __str__(self):
        return f"{self.full_name} - {self.policy.policy_number}"

