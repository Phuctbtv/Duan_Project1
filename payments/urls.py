from django.urls import path
from payments.views import payments_users, calculate_premium, process_payment

urlpatterns = [
    path("", payments_users, name="payments_users"),
    path("api/calculate-premium/", calculate_premium, name="calculate_premium"),
    path("api/process/", process_payment, name="process_payment"),
]
