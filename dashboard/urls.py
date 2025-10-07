from . import views
from django.urls import path
urlpatterns = [
    path('admin/', views.admin_home, name='admin_home'),
    path('customers/', views.custom_section, name='custom_section'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:user_id>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:user_id>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:user_id>/toggle-status/', views.customer_toggle_status, name='customer_toggle_status'),
    path('customers/<int:user_id>/delete/', views.customer_delete, name='customer_delete'),
]
