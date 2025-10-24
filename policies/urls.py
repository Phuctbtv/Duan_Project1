
from django.urls import path
from . import views

urlpatterns = [
    # ADMIN
    path('admin/policies/', views.custom_policies_admin, name='custom_policies_admin'),

    # Danh sách hợp đồng
    path('admin/policies/list/', views.admin_policy_list, name='admin_policy_list'),

    # Tạo hợp đồng mới
    path('admin/policies/add/', views.admin_policy_create, name='policy_create'),

    # Xem chi tiết hợp đồng
    path('admin/policies/<int:pk>/', views.admin_policy_detail, name='policy_detail'),
    path('api/<int:pk>/detail/', views.api_policy_detail, name='api_policy_detail'),

    # Gia hạn hợp đồng
    path('admin/policies/<int:pk>/renew/', views.admin_policy_renew, name='policy_renew'),

    # Hủy hợp đồng
    path('admin/policies/<int:pk>/cancel/', views.admin_policy_cancel, name='policy_delete'),
    # Sửa hợp đồng
    path('admin/policies/<int:pk>/edit/', views.admin_policy_edit, name='policy_edit'),
    # Duyệt/Từ chối hợp đồng
    path('api/<int:pk>/approve/', views.api_approve_policy, name='api_approve_policy'),
    path('api/<int:pk>/reject/', views.api_reject_policy, name='api_reject_policy'),
    # USER
    path('user/policies/dashboard/', views.dashboard_view_user, name='custom_policies_users'),

]


