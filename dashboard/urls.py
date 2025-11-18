



from django.urls import path
from . import views
from .views import custom_section
from .views import CheckUsernameView, CheckEmailView


urlpatterns = [
    path('', views.admin_home, name='admin_home'),
    path('data/', views.dashboard_data, name='dashboard_data'),
    path("admin/customser/", views.custom_section, name="custom_section"),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:user_id>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:user_id>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:user_id>/toggle-status/', views.customer_toggle_status, name='customer_toggle_status'),
    path('customers/<int:user_id>/convert-role/', views.customer_convert_role, name='customer_convert_role'),

    path('agents/create/', views.agent_create, name='agent_create'),
    path('agents/<int:user_id>/', views.agent_detail, name='agent_detail'),
    path('agents/<int:user_id>/edit/', views.agent_edit, name='agent_edit'),
    path('agents/<int:user_id>/toggle-status/', views.agent_toggle_status, name='agent_toggle_status'),
    path('check-username/', CheckUsernameView.as_view(), name='check_username'),
    path('check-email/', CheckEmailView.as_view(), name='check_email'),
]