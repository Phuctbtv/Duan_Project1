from django.urls import path
from . import views
from .views import custom_section

urlpatterns = [
    path('', views.admin_home, name='admin_home'),
    path('data/', views.dashboard_data, name='dashboard_data'),
    path("customser/", views.custom_section, name="custom_section"),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:user_id>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:user_id>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:user_id>/toggle-status/', views.customer_toggle_status, name='customer_toggle_status'),
    path('customers/<int:user_id>/delete/', views.customer_delete, name='customer_delete'),
    path('customer/<int:user_id>/convert-role/', views.customer_convert_role, name='customer_convert_role'),
]