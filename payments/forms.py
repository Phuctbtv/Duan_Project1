
from django import forms
from datetime import date


class HealthInfoForm(forms.Form):

    GENDER_CHOICES = [('male', 'Nam'), ('female', 'Nữ')]
    SMOKING_CHOICES = [('never', 'Không hút'), ('former', 'Đã bỏ'), ('current', 'Đang hút')]
    ALCOHOL_CHOICES = [('no', 'Không'), ('sometimes', 'Thỉnh thoảng')]
    RELATIONSHIP_CHOICES = [
        ('spouse', 'Vợ/Chồng'), ('child', 'Con'),
        ('parent', 'Cha/Mẹ'), ('sibling', 'Anh/Chị/Em'),('me','Chính mình')
    ]
    CONDITIONS_CHOICES = [
        ('tiểu_đường', 'Tiểu đường'),
        ('tim_mạch_cao_huyết_áp', 'Tim mạch / Cao huyết áp'),
        ('ung_thư_thận_gan_phổi', 'Ung thư / Thận / Gan / Phổi'),
        ('đang_điều_trị_dài_hạn', 'Đang điều trị dài hạn'),
    ]

    # --- Thông tin cơ bản ---
    fullname = forms.CharField(label='Họ và tên', max_length=100, required=True)
    birthDate = forms.DateField(label='Ngày sinh', required=True)
    age = forms.IntegerField(label='Tuổi', required=False)
    id_card_number = forms.CharField(label='CCCD/CMND', max_length=20, required=False)
    gender = forms.ChoiceField(label='Giới tính', choices=GENDER_CHOICES, required=True)
    occupation = forms.CharField(label='Nghề nghiệp', max_length=100, required=True)

    # --- Thông tin sức khỏe ---
    height = forms.IntegerField(label='Chiều cao (cm)', required=True)
    weight = forms.IntegerField(label='Cân nặng (kg)', required=True)
    smoker = forms.ChoiceField(label='Hút thuốc', choices=SMOKING_CHOICES, required=True)
    alcohol = forms.ChoiceField(label='Uống rượu/bia', choices=ALCOHOL_CHOICES, required=True)

    # --- Tiền sử bệnh lý (dùng MultipleChoiceField cho checkboxes) ---
    conditions = forms.MultipleChoiceField(
        label='Tiền sử bệnh lý',
        choices=CONDITIONS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    # --- Người thụ hưởng ---
    sameBeneficiary = forms.BooleanField(required=False)
    fullname_benefic = forms.CharField(label='Họ tên người thụ hưởng', max_length=100, required=False)
    relationship_to_customer = forms.ChoiceField(label='Mối quan hệ', choices=RELATIONSHIP_CHOICES, required=False)
    birthDate_benefic = forms.DateField(label='Ngày sinh người thụ hưởng', required=False)
    id_card_number_benefic = forms.CharField(label='CCCD/CMND người thụ hưởng', max_length=20, required=False)

    # --- Thông tin liên hệ ---
    phone = forms.CharField(label='Số điện thoại', max_length=11, required=True)
    email = forms.EmailField(label='Email', required=True)
    address = forms.CharField(label='Địa chỉ', max_length=255, required=True)

    # --- Validate logic phức tạp ---
    def clean(self):
        cleaned_data = super().clean()
        is_same_beneficiary = cleaned_data.get('sameBeneficiary')

        # Nếu người mua không phải là người thụ hưởng, thì các trường thông tin
        # của người thụ hưởng trở thành bắt buộc.
        if not is_same_beneficiary:
            required_fields = {
                'fullname_benefic': "Họ tên người thụ hưởng là bắt buộc.",
                'relationship_to_customer': "Mối quan hệ là bắt buộc.",
                'birthDate_benefic': "Ngày sinh người thụ hưởng là bắt buộc.",
            }
            for field, message in required_fields.items():
                if not cleaned_data.get(field):
                    self.add_error(field, message)

        # Validate tuổi (ví dụ: phải trên 18)
        birth_date = cleaned_data.get('birthDate')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                self.add_error('birthDate', 'Bạn phải đủ 18 tuổi để mua bảo hiểm.')

        return cleaned_data