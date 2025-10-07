from django import forms
from .models import Policy
from users.models import Customer
from insurance_products.models import InsuranceProduct

class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        # chỉ để các trường cần nhập
        fields = [
            "customer",
            "product",
            "policy_number",
            "start_date",
            "end_date",
            "premium_amount",
            "sum_insured",
            "policy_document_url",
            "payment_status",
            "policy_status",
            "claimed_amount",  # thêm vào đây
        ]
        widgets = {
            "customer": forms.Select(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            }),
            "product": forms.Select(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            }),
            "policy_number": forms.TextInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            }),
            "start_date": forms.DateInput(attrs={
                "type": "date",
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            }),
            "end_date": forms.DateInput(attrs={
                "type": "date",
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            }),
            "premium_amount": forms.NumberInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            }),
            "sum_insured": forms.NumberInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            }),
            # "policy_document_url": forms.FileInput(attrs={
            #     "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            # }),
            "policy_document_url": forms.URLInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500",
                "placeholder": "Nhập URL tài liệu hợp đồng"
            }),

            "payment_status": forms.Select(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            }),
            "policy_status": forms.Select(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            }),
            "claimed_amount": forms.NumberInput(attrs={  # widget cho claimed_amount
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500",
                "placeholder": "Nhập tổng số tiền đã chi trả"
            }),
        }
