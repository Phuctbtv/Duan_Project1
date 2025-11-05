# app_claims/urls.py
from django.urls import path, include
from .views import custom_claims_user, filter_claims_ajax, create_claims, detail_claims, add_additional_documents, \
    custom_claims_admin, get_all_claims

urlpatterns = [
    path('', custom_claims_user, name='custom_claims_user'),
    path("api/filter/",filter_claims_ajax, name="filter_claims_ajax"),
    path("create_claims/<int:pk>/",create_claims, name="create_claims"),
    path("detail_claims/<int:pk>/",detail_claims, name="detail_claims"),
    path('add-documents/<str:claim_number>/', add_additional_documents, name='add_additional_documents'),
    path("admin/",custom_claims_admin, name='custom_claims_admin'),
    path("api/claims/",get_all_claims, name='get_all_claims_api'),
]
