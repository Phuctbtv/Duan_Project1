from django.db import models
from policies.models import Policy


class Payment(models.Model):
    """Model thanh toán"""

    PAYMENT_METHOD_CHOICES = [
        ("credit_card", "Thẻ tín dụng"),
        ("bank_transfer", "Chuyển khoản ngân hàng"),
        ("e_wallet", "Ví điện tử"),
        ("money","Tiền mặt"),
        ("other", "Khác"),
    ]

    STATUS_CHOICES = [
        ("success", "Thành công"),
        ("failed", "Thất bại"),
        ("pending", "Chờ xử lý"),
    ]

    policy = models.ForeignKey(
        Policy, on_delete=models.CASCADE, verbose_name="Hợp đồng bảo hiểm", related_name="payments"
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Số tiền"
    )
    payment_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Ngày thanh toán"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="Phương thức thanh toán",
    )
    transaction_id = models.CharField(
        max_length=100, unique=True, verbose_name="Mã giao dịch"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Trạng thái",
    )

    class Meta:
        db_table = "payment"
        verbose_name = "Thanh toán"
        verbose_name_plural = "Thanh toán"

    def __str__(self):
        return f"{self.transaction_id} - {self.amount}"
