from django.urls import path
from . import views

urlpatterns = [
    path('admin/policies/', views.custom_policies_admin, name='custom_policies_admin'),
    path('user/policies/dashboard', views.dashboard_view_user, name='custom_policies_users'),
]
