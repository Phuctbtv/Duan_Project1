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
        Policy, on_delete=models.CASCADE,related_name="claims", verbose_name="Hợp đồng bảo hiểm"
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
        max_digits=15, decimal_places=2, verbose_name="Số tiền yêu cầu"
    )
    claimed_amount = models.DecimalField(
        max_digits=15,
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
        max_digits=15,
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

class ClaimMedicalInfo(models.Model):
    """Thông tin y tế liên quan đến yêu cầu bồi thường"""

    TREATMENT_TYPE_CHOICES = [
        ("inpatient", "Điều trị nội trú"),
        ("outpatient", "Điều trị ngoại trú"),
        ("surgery", "Phẫu thuật"),
        ("death", "Tử vong"),
        ("other", "Khác"),
    ]

    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name="claim_medical_info")
    treatment_type = models.CharField(max_length=20, choices=TREATMENT_TYPE_CHOICES, verbose_name="Loại điều trị")
    hospital_name = models.CharField(max_length=255, verbose_name="Tên bệnh viện / cơ sở y tế")
    doctor_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Bác sĩ điều trị")
    hospital_address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Địa chỉ bệnh viện")
    diagnosis = models.TextField(blank=True, null=True, verbose_name="Chẩn đoán / bệnh lý")
    admission_date = models.DateField(blank=True, null=True, verbose_name="Ngày nhập viện")
    discharge_date = models.DateField(blank=True, null=True, verbose_name="Ngày xuất viện")

    total_treatment_cost = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Tổng chi phí điều trị"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        db_table = "claim_medical_info"
        verbose_name = "Thông tin y tế"
        verbose_name_plural = "Thông tin y tế"

    def __str__(self):
        return f"Y tế cho yêu cầu #{self.claim.id} - {self.hospital_name}"


class ClaimDocument(models.Model):
    """Model tài liệu bồi thường"""

    claim = models.ForeignKey(
        Claim, on_delete=models.CASCADE, verbose_name="Yêu cầu bồi thường", related_name="claim_documents"
    )
    document_type = models.CharField(max_length=50, verbose_name="Loại tài liệu")
    file_url = models.FileField(verbose_name="URL file")
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

class ClaimPayment(models.Model):
    claim = models.OneToOneField("Claim", on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=100, verbose_name="Ngân hàng")
    account_number = models.CharField(max_length=30, verbose_name="Số tài khoản")
    account_holder_name = models.CharField(max_length=100, verbose_name="Chủ tài khoản")

    class Meta:
        db_table = "claim_payment"
        verbose_name = "Tài khoản nhận bồi thường"
        verbose_name_plural = "Tài khoản nhận bồi thường"

    def __str__(self):
        return f"{self.account_holder_name} - {self.bank_name}"


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
