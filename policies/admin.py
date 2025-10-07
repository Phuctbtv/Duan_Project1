from django.contrib import admin
from .models import Policy, PolicyHolder

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = (
        'policy_number',
        'customer_name',
        'product_name',
        'sum_insured_short',
        'premium_short',
        'payment_status',
        'policy_status',
        'start_date',
        'end_date',
        'remaining_days',
    )
    list_filter = ('payment_status', 'policy_status', 'start_date', 'end_date')
    search_fields = ('policy_number', 'customer__user__username', 'product__product_name')
    ordering = ('-start_date',)
    list_per_page = 20

    def customer_name(self, obj):
        return obj.customer.user.get_full_name() or obj.customer.user.username
    customer_name.short_description = "Khách hàng"

    def product_name(self, obj):
        return obj.product.product_name
    product_name.short_description = "Sản phẩm"

@admin.register(PolicyHolder)
class PolicyHolderAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'policy', 'date_of_birth', 'relationship_to_customer')
    search_fields = ('full_name', 'policy__policy_number')
    list_filter = ('relationship_to_customer',)
