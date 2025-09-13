from django.urls import path
from . import views

urlpatterns = [
    path('admin/policies/', views.custom_policies_admin, name='custom_policies_admin'),
    path('user/policies/', views.custom_policies_users, name='custom_policies_users'),
]
