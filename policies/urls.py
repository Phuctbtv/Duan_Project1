# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('admin/policies/', views.custom_policies_admin, name='custom_policies_admin'),
#     path('user/policies/dashboard', views.dashboard_view_user, name='custom_policies_users'),
# ]
#
#
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

    # Gia hạn hợp đồng
    path('admin/policies/<int:pk>/renew/', views.admin_policy_renew, name='policy_renew'),

    # Hủy hợp đồng
    path('admin/policies/<int:pk>/cancel/', views.admin_policy_cancel, name='policy_delete'),
    # Sửa hợp đồng - THÊM DÒNG NÀY
    path('admin/policies/<int:pk>/edit/', views.admin_policy_edit, name='policy_edit'),

    # USER
    path('user/policies/dashboard/', views.dashboard_view_user, name='custom_policies_users'),

]


