from django import forms
from .models import InsuranceProduct
from django.utils import timezone

class InsuranceProductForm(forms.ModelForm):
    class Meta:
        model = InsuranceProduct
        fields = [
            'product_name',
            'description',
            'coverage_details',
            'terms_and_conditions',
            'premium_base_amount',
            'currency',
            'max_claim_amount',
            "agent_commission_percent",
            'product_type',
        ]

        labels = {
            'product_name': 'Tên sản phẩm',
            'description': 'Mô tả',
            'coverage_details': 'Chi tiết phạm vi bảo hiểm',
            'terms_and_conditions': 'Điều khoản và điều kiện',
            'premium_base_amount': 'Phí bảo hiểm cơ bản',
            'currency': 'Đơn vị tiền tệ',
            'max_claim_amount': 'Số tiền bồi thường tối đa',
            "agent_commission_percent" : 'Phí hoa hồng(%)',
            'product_type': 'Loại sản phẩm',
        }

        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'coverage_details': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'terms_and_conditions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'premium_base_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'max_claim_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'agent_commission_percent': forms.NumberInput(attrs={'class': 'form-control'}),
            'product_type': forms.TextInput(attrs={'class': 'form-control'}),
        }

    # ✅ Ghi đè phương thức save để tự động cập nhật 3 trường đặc biệt
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.is_active = True  # luôn active
        instance.updated_at = timezone.now()
        if not instance.created_at:
            instance.created_at = timezone.now()
        if commit:
            instance.save()
        return instance
