from django.urls import path
from payments.views import payments_users
urlpatterns = [
    path("", payments_users, name="payments_users"),
]
