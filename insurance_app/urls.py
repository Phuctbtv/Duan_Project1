from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', include('dashboard.urls')),
    path('insurance_products/', include('insurance_products.urls')),
    path("",include("users.urls")),
    path("custom_products/", include("insurance_products.urls")),
    path("custom_policies/", include("policies.urls")),
    path("payments/", include("payments.urls")),
    path("custom_claims/", include("claims.urls")),
]
