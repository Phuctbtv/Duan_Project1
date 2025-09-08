from django.urls import path
from . import views
from django.urls import path, include
urlpatterns = [
    path('', views.admin_home, name='admin_home'),
    path("customer_users/",include("users.urls")),
    path("customer_products/", include("insurance_products.urls")),
    path("customer_policies/", include("policies.urls")),
    path("customer_payments/", include("payments.urls")),
    path("customer_claims/", include("claims.urls")),
]
