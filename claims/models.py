from django.db import models
from users.models import Customer
from policies.models import Policy


class Claim(models.Model):
    """Model yêu cầu bồi thường"""

    CLAIM_STATUS_CHOICES = [
        ("pending", "Chờ xử lý"),
        ("in_progress", "Đang xử lý"),
        ("approved", "Đã duyệt"),
        ("rejected", "Từ chối"),
        ("settled", "Đã giải quyết"),
    ]

    policy = models.ForeignKey(
        Policy, on_delete=models.CASCADE, verbose_name="Hợp đồng bảo hiểm"
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, verbose_name="Khách hàng"
    )
    claim_number = models.CharField(
        max_length=50, unique=True, null=True, blank=True, verbose_name="Số yêu cầu bồi thường"
    )
    claim_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Ngày gửi yêu cầu"
    )
    incident_date = models.DateField(verbose_name="Ngày xảy ra sự cố")
    description = models.TextField(verbose_name="Mô tả sự cố")
    requested_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Số tiền yêu cầu"
    )
    claimed_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Tổng số tiền đã chi trả",
        null=True, blank=True
    )
    claim_status = models.CharField(
        max_length=15,
        choices=CLAIM_STATUS_CHOICES,
        default="pending",
        verbose_name="Trạng thái yêu cầu",
    )
    approved_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Số tiền được duyệt",
    )
    rejection_reason = models.TextField(blank=True, verbose_name="Lý do từ chối")
    settlement_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Ngày giải quyết"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        db_table = "claims"
        verbose_name = "Yêu cầu bồi thường"
        verbose_name_plural = "Yêu cầu bồi thường"

    def __str__(self):
        return f"Yêu cầu #{self.id} - {self.customer.user.first_name} {self.customer.user.last_name}"


class ClaimDocument(models.Model):
    """Model tài liệu bồi thường"""

    claim = models.ForeignKey(
        Claim, on_delete=models.CASCADE, verbose_name="Yêu cầu bồi thường"
    )
    document_type = models.CharField(max_length=50, verbose_name="Loại tài liệu")
    file_url = models.URLField(verbose_name="URL file")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tải lên")
    ocr_extracted_text = models.TextField(blank=True, verbose_name="Văn bản OCR")
    ai_analysis_result = models.JSONField(
        default=dict, verbose_name="Kết quả phân tích AI"
    )

    class Meta:
        db_table = "claimdocuments"
        verbose_name = "Tài liệu bồi thường"
        verbose_name_plural = "Tài liệu bồi thường"

    def __str__(self):
        return f"{self.document_type} - Yêu cầu #{self.claim.id}"


class RiskAssessment(models.Model):
    """Model đánh giá rủi ro"""

    RISK_LEVEL_CHOICES = [
        ("low", "Thấp"),
        ("medium", "Trung bình"),
        ("high", "Cao"),
        ("very_high", "Rất cao"),
    ]

    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Hợp đồng bảo hiểm",
    )
    claim = models.ForeignKey(
        Claim,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Yêu cầu bồi thường",
    )
    assessment_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Ngày đánh giá"
    )
    risk_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Điểm rủi ro"
    )
    risk_level = models.CharField(
        max_length=10, choices=RISK_LEVEL_CHOICES, verbose_name="Mức độ rủi ro"
    )
    ai_model_version = models.CharField(
        max_length=50, verbose_name="Phiên bản mô hình AI"
    )
    assessment_details = models.JSONField(
        default=dict, verbose_name="Chi tiết đánh giá"
    )

    class Meta:
        db_table = "riskassessments"
        verbose_name = "Đánh giá rủi ro"
        verbose_name_plural = "Đánh giá rủi ro"

    def __str__(self):
        target = self.policy or self.claim
        return f"Đánh giá rủi ro - {target} - {self.risk_level}"
