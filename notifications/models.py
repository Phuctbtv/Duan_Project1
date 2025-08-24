from django.db import models
from users.models import User


class Notification(models.Model):
    """Model thông báo"""

    NOTIFICATION_TYPE_CHOICES = [
        ("policy_update", "Cập nhật hợp đồng"),
        ("claim_status", "Trạng thái bồi thường"),
        ("payment_reminder", "Nhắc nhở thanh toán"),
        ("promotion", "Khuyến mãi"),
        ("other", "Khác"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Người dùng")
    message = models.TextField(verbose_name="Nội dung thông báo")
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPE_CHOICES, verbose_name="Loại thông báo"
    )
    is_read = models.BooleanField(default=False, verbose_name="Đã đọc")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian gửi")

    class Meta:
        db_table = "notification"
        verbose_name = "Thông báo"
        verbose_name_plural = "Thông báo"
        ordering = ["-sent_at"]

    def __str__(self):
        return f"Thông báo cho {self.user.full_name} - {self.notification_type}"
