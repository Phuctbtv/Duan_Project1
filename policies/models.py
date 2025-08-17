from django.db import models
from users.models import Customer
from insurance_products.models import InsuranceProduct


class Policy(models.Model):
    """Model hợp đồng bảo hiểm"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Chờ thanh toán'),
        ('paid', 'Đã thanh toán'),
        ('overdue', 'Quá hạn'),
        ('cancelled', 'Đã hủy'),
    ]

    POLICY_STATUS_CHOICES = [
        ('active', 'Đang hoạt động'),
        ('expired', 'Đã hết hạn'),
        ('cancelled', 'Đã hủy'),
        ('pending', 'Chờ xử lý'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        verbose_name="Khách hàng"
    )
    product = models.ForeignKey(
        InsuranceProduct,
        on_delete=models.CASCADE,
        verbose_name="Sản phẩm bảo hiểm"
    )
    policy_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Số hợp đồng"
    )
    start_date = models.DateField(verbose_name="Ngày hiệu lực")
    end_date = models.DateField(verbose_name="Ngày hết hạn")
    premium_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Phí bảo hiểm"
    )
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái thanh toán"
    )
    policy_status = models.CharField(
        max_length=10,
        choices=POLICY_STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái hợp đồng"
    )
    policy_document_url = models.URLField(
        blank=True,
        verbose_name="URL tài liệu hợp đồng"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Hợp đồng bảo hiểm"
        verbose_name_plural = "Hợp đồng bảo hiểm"

    def __str__(self):
        return f"{self.policy_number} - {self.customer.user.full_name}"


class PolicyHolder(models.Model):
    """Model người được bảo hiểm"""
    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        verbose_name="Hợp đồng bảo hiểm"
    )
    full_name = models.CharField(max_length=100, verbose_name="Họ và tên")
    date_of_birth = models.DateField(verbose_name="Ngày sinh")
    id_card_number = models.CharField(max_length=20, verbose_name="Số CMND/CCCD")
    relationship_to_customer = models.CharField(
        max_length=50,
        verbose_name="Mối quan hệ với khách hàng"
    )

    class Meta:
        db_table = "PolicyHolder"
        verbose_name = "Người được bảo hiểm"
        verbose_name_plural = "Người được bảo hiểm"

    def __str__(self):
        return f"{self.full_name} - {self.policy.policy_number}"