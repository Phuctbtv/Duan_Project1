
from django.urls import path

from policies.views import custom_policies_admin, admin_policy_list, admin_policy_detail, \
    api_policy_detail, admin_policy_renew, admin_policy_cancel, admin_policy_edit, api_approve_policy, \
    api_reject_policy, dashboard_view_user, transfer_servicing_agent_api

urlpatterns = [
    # ADMIN
    path('admin/policies/',custom_policies_admin, name='custom_policies_admin'),

    # Danh sách hợp đồng
    path('admin/policies/list/', admin_policy_list, name='admin_policy_list'),

    # Xem chi tiết hợp đồng
    path('admin/policies/<int:pk>/', admin_policy_detail, name='policy_detail'),
    path('api/<int:pk>/detail/', api_policy_detail, name='api_policy_detail'),

    # Gia hạn hợp đồng
    path('admin/policies/<int:pk>/renew/', admin_policy_renew, name='policy_renew'),

    # Hủy hợp đồng
    path('admin/policies/<int:pk>/cancel/', admin_policy_cancel, name='policy_delete'),
    # Sửa hợp đồng
    path('admin/policies/<int:pk>/edit/', admin_policy_edit, name='policy_edit'),
    # Duyệt/Từ chối hợp đồng
    path('api/<int:pk>/approve/', api_approve_policy, name='api_approve_policy'),
    path('api/<int:pk>/reject/', api_reject_policy, name='api_reject_policy'),
    path('api/policy/<int:pk>/transfer-agent/',transfer_servicing_agent_api, name='transfer_servicing_agent_api'),
    # USE
    path('user/policies/dashboard/', dashboard_view_user, name='custom_policies_users'),

]


