# app_claims/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from claims.views import custom_claims_user, filter_claims_ajax, create_claims

urlpatterns = [
    path('', custom_claims_user, name='custom_claims_user'),
    path("api/filter/",filter_claims_ajax, name="filter_claims_ajax"),
    path("create_claims/<int:pk>/",create_claims, name="create_claims"),
]
