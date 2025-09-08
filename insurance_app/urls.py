from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', include('dashboard.urls')),
    path("", include("users.urls")),
    path("payments/", include("payments.urls")),
]
