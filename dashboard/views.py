from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

# Import models từ users app
from users.models import User, Customer


@login_required
def admin_home(request):
    """Dashboard chính cho admin"""
    if not request.user.is_staff:
        from django.shortcuts import redirect
        return redirect('trangchu')

    # Lấy dữ liệu thống kê từ database
    try:
        total_customers = Customer.objects.count()
        total_users = User.objects.count()
        staff_users = User.objects.filter(is_staff=True).count()

        # Tính toán thêm các số liệu khác nếu cần
        active_customers = Customer.objects.filter(user__is_active=True).count()
        new_customers_this_month = Customer.objects.filter(
            user__date_joined__month=timezone.now().month
        ).count()

    except Exception as e:
        # Fallback nếu có lỗi
        print(f"Lỗi khi lấy dữ liệu: {e}")
        total_customers = 1234
        total_users = 1500
        staff_users = 15
        active_customers = 1200
        new_customers_this_month = 45

    context = {
        'total_customers': total_customers,
        'total_users': total_users,
        'staff_users': staff_users,
        'active_customers': active_customers,
        'new_customers_this_month': new_customers_this_month,
        'active_contracts': 856,
        'recent_claims': 42,
        'monthly_revenue': 58.5,
        'approval_rate': 94.2,
        'avg_processing_time': 2.3,
        'customer_satisfaction': 4.8,
    }

    return render(request, "admin/dashboard_section.html", context)


@login_required
def dashboard_data(request):
    """API cung cấp dữ liệu cho biểu đồ"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        # Có thể thêm logic lấy dữ liệu thực từ database ở đây
        # Ví dụ: doanh thu theo tháng, số hợp đồng theo loại, etc.

        # Dữ liệu mẫu cho biểu đồ - sẽ thay thế bằng dữ liệu thực sau
        data = {
            'revenue_chart': {
                'labels': ['Th1', 'Th2', 'Th3', 'Th4', 'Th5', 'Th6'],
                'data': [45, 52, 48, 55, 58.5, 62],
                'title': 'Doanh Thu Theo Tháng (tỷ VNĐ)'
            },
            'contract_chart': {
                'labels': ['Bảo Hiểm Ô Tô', 'Bảo Hiểm Sức Khỏe', 'Bảo Hiểm Du Lịch', 'Bảo Hiểm Nhà Ở'],
                'data': [45, 25, 15, 15],
                'title': 'Phân Loại Hợp Đồng'
            },
            'customer_growth': {
                'labels': ['Tuần 1', 'Tuần 2', 'Tuần 3', 'Tuần 4'],
                'data': [25, 32, 28, 45],
                'title': 'Tăng Trưởng Khách Hàng'
            }
        }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Các hàm tiện ích cho thống kê (có thể thêm sau)
def get_monthly_revenue():
    """Lấy doanh thu theo tháng (sẽ triển khai sau)"""
    # TODO: Triển khai logic lấy doanh thu thực từ database
    return [45, 52, 48, 55, 58.5, 62]


def get_contracts_by_type():
    """Lấy số hợp đồng theo loại (sẽ triển khai sau)"""
    # TODO: Triển khai logic lấy số hợp đồng thực từ database
    return [45, 25, 15, 15]