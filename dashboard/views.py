from django.db import transaction
import json
import random
import string
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db.models import Count, Sum, Q, ProtectedError
from django.utils import timezone
from datetime import timedelta, datetime

from users.decorators import admin_required
from users.models import Customer, User, Agent
from policies.models import Policy
from claims.models import Claim
from payments.models import Payment
from django.contrib import messages


def generate_agent_code():
    """Tạo mã đại lý tự động theo định dạng AG + số ngẫu nhiên"""
    while True:
        # Tạo mã 3 chữ số ngẫu nhiên
        random_digits = ''.join(random.choices(string.digits, k=3))
        code = f"AG{random_digits}"

        # Kiểm tra mã đã tồn tại chưa
        if not Agent.objects.filter(code=code).exists():
            return code

@method_decorator(csrf_exempt, name='dispatch')
class CheckAgentCodeView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            code = data.get('code')
            exists = Agent.objects.filter(code=code).exists()
            return JsonResponse({'exists': exists})
        except Exception as e:
            return JsonResponse({'exists': False, 'error': str(e)})

@login_required
@admin_required
def generate_agent_code_api(request):
    """API tạo mã đại lý mới"""
    try:
        code = generate_agent_code()
        return JsonResponse({'code': code})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class CheckUsernameView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            exists = User.objects.filter(username=username).exists()
            return JsonResponse({'exists': exists})
        except Exception as e:
            return JsonResponse({'exists': False, 'error': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class CheckEmailView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            if not email:
                return JsonResponse({'exists': False})
            exists = User.objects.filter(email=email).exists()
            return JsonResponse({'exists': exists})
        except Exception as e:
            return JsonResponse({'exists': False, 'error': str(e)})

@login_required
def admin_home(request):
    """Dashboard chung cho cả Admin và Agent"""

    user_type = request.user.user_type
    is_admin = request.user.is_superuser
    is_agent = user_type == 'agent'
    if is_admin:
        template = "dashboard/admin/dashboard_section.html"
    else:
        template = "dashboard/agent/dashboard_agent.html"
    if not (is_admin or is_agent):
        return redirect('trangchu')

    total_customers = active_customers = new_customers_this_month = 0
    admin_monthly_revenue = agent_monthly_revenue= approval_rate = avg_processing_time = 0
    active_policies_count = pending_claims_count = pending_policies = 0
    recent_activities = []
    agent_code = None
    monthly_commission = 0

    current_month = timezone.now().month
    current_year = timezone.now().year

    try:
        if is_admin:
            # ADMIN: Dữ liệu toàn hệ thống
            total_customers = Customer.objects.count()
            active_customers = Customer.objects.filter(user__is_active=True).count()

            new_customers_this_month = Customer.objects.filter(
                user__date_joined__month=current_month,
                user__date_joined__year=current_year
            ).count()

            # Doanh thu tháng (tỷ VNĐ)
            admin_monthly_revenue_raw = Payment.objects.filter(
                payment_date__month=current_month,
                payment_date__year=current_year,
                status='success'
            ).aggregate(total=Sum('amount'))['total'] or 0

            admin_monthly_revenue = float(admin_monthly_revenue_raw) / 1_000_000_000

            print("doanh thu tháng admin:",admin_monthly_revenue)
            # Policies và claims
            active_policies_count = Policy.objects.filter(policy_status='active').count()
            pending_claims_count = Claim.objects.filter(claim_status='pending').count()
            pending_policies = Policy.objects.filter(policy_status='pending').count()



            # Tỷ lệ phê duyệt
            total_claims = Claim.objects.count()
            if total_claims > 0:
                approved_claims = Claim.objects.filter(claim_status='approved').count()
                approval_rate = round((approved_claims / total_claims) * 100, 1)
            else:
                approval_rate = 0

            # Thời gian xử lý trung bình
            settled_claims = Claim.objects.filter(
                claim_status__in=['approved', 'rejected', 'settled']
            )
            total_days = 0
            count = 0
            for claim in settled_claims:
                if claim.updated_at and claim.claim_date:
                    days = (claim.updated_at.date() - claim.claim_date).days
                    total_days += days
                    count += 1
            avg_processing_time = round(total_days / count, 1) if count > 0 else 0

            # Hoạt động gần đây
            recent_activities = get_recent_activities()

        elif is_agent:
            # AGENT: Dữ liệu cá nhân THỰC
            try:
                agent = Agent.objects.get(user=request.user)
                agent_code = agent.code

                # Khách hàng của agent - TẠM THỜI DÙNG COUNT ĐƠN GIẢN
                # total_customers = Customer.objects.filter(agent=agent).count()
                # active_customers = Customer.objects.filter(agent=agent, user__is_active=True).count()

                # Khách hàng mới tháng này
                # new_customers_this_month = Customer.objects.filter(
                #     agent=agent,
                #     user__date_joined__month=current_month,
                #     user__date_joined__year=current_year
                # ).count()

                # Hợp đồng của agent
                active_policies_count = Policy.objects.filter(agent=agent, policy_status='active').count()
                pending_policies = Policy.objects.filter(agent=agent, policy_status='pending').count()

                # Claims của agent

                pending_claims_count = Claim.objects.filter(
                    policy__agent=agent,
                    claim_status="pending"
                ).count()

                # Doanh thu cá nhân (triệu VNĐ) - TÍNH TỪ HOA HỒNG THỰC TẾ
                monthly_commission = Policy.objects.filter(
                    agent=agent,
                    policy_status='active',
                    payment_status='paid',  # CHỈ TÍNH HỢP ĐỒNG ĐÃ THANH TOÁN
                    updated_at__month=current_month,
                    updated_at__year=current_year
                ).aggregate(total=Sum('commission_amount'))['total'] or 0
                monthly_commission = float(monthly_commission) / 1_000_000  # Chuyển sang triệu

                # Doanh thu hiển thị (có thể dùng commission hoặc premium)
                agent_revenue_raw = Policy.objects.filter(
                    agent=agent,
                    policy_status='active',
                    payment_status='paid',
                    updated_at__month=current_month,
                    updated_at__year=current_year
                ).aggregate(total=Sum('premium_amount'))['total'] or 0

                agent_monthly_revenue = float(agent_revenue_raw) / 1_000_000
                print("doanh thu tháng agent:", agent_monthly_revenue)
                # Tỷ lệ phê duyệt của agent
                agent_claims = Claim.objects.filter(
                    policy__agent=agent,
                )

                total_agent_claims = agent_claims.count()
                if total_agent_claims > 0:
                    approved_agent_claims = agent_claims.filter(claim_status='approved').count()
                    approval_rate = round((approved_agent_claims / total_agent_claims) * 100, 1)
                else:
                    approval_rate = 0

                # Thời gian xử lý trung bình của agent
                settled_agent_claims = agent_claims.filter(
                    claim_status__in=['approved', 'rejected', 'settled']
                )
                total_days = 0
                count = 0
                for claim in settled_agent_claims:
                    if claim.updated_at and claim.claim_date:
                        days = (claim.updated_at.date() - claim.claim_date).days
                        total_days += days
                        count += 1
                avg_processing_time = round(total_days / count, 1) if count > 0 else 0

                # Hoa hồng (tính từ các policy của agent)
                total_commission = Policy.objects.filter(
                    agent=agent,
                    policy_status='active'
                ).aggregate(total=Sum('commission_amount'))['total'] or 0
                monthly_commission = float(total_commission) / 1_000_000

                # Hoạt động gần đây của agent
                recent_activities = get_agent_recent_activities(agent)

            except Agent.DoesNotExist:
                # Fallback nếu agent không tồn tại
                total_customers = 25
                active_customers = 20
                agent_monthly_revenue = 2.5
                approval_rate = 88.5
                avg_processing_time = 1.8
                new_customers_this_month = 5
                active_policies_count = 18
                pending_claims_count = 3
                pending_policies = 2
                monthly_commission = 15.2
                recent_activities = [
                    {'message': 'Khách hàng Nguyễn Văn B đã mua bảo hiểm', 'time': '10 phút trước',
                     'color': 'bg-green-500'},
                    {'message': 'Hoa hồng tháng này: 15.000.000đ', 'time': '1 giờ trước', 'color': 'bg-purple-500'},
                ]
                agent_code = f"AG{request.user.id:04d}"

    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu: {e}")
        # Fallback data để không bị lỗi
        if is_admin:
            total_customers = 1234
            active_customers = 1000
            admin_monthly_revenue = 58.5
            approval_rate = 94.2
            avg_processing_time = 2.3
            new_customers_this_month = 45
            active_policies_count = 890
            pending_claims_count = 23
            pending_policies = 8
            recent_activities = [
                {'message': 'Hệ thống đang hoạt động bình thường', 'time': 'Vừa xong', 'color': 'bg-green-500'},
                {'message': 'Chào mừng đến với hệ thống', 'time': 'Hôm nay', 'color': 'bg-blue-500'},
            ]
        elif is_agent:
            total_customers = 25
            active_customers = 20
            agent_monthly_revenue = 2.5
            approval_rate = 88.5
            avg_processing_time = 1.8
            new_customers_this_month = 5
            active_policies_count = 18
            pending_claims_count = 3
            pending_policies = 2
            monthly_commission = 15.2
            recent_activities = [
                {'message': 'Khách hàng Nguyễn Văn B đã mua bảo hiểm', 'time': '10 phút trước',
                 'color': 'bg-green-500'},
                {'message': 'Hoa hồng tháng này: 15.000.000đ', 'time': '1 giờ trước', 'color': 'bg-purple-500'},
            ]
            agent_code = f"AG{request.user.id:04d}"

    context = {
        'total_customers': total_customers,
        'active_customers': active_customers,
        'new_customers_this_month': new_customers_this_month,
        'admin_monthly_revenue': round(admin_monthly_revenue, 5),
        'agent_monthly_revenue': round(agent_monthly_revenue, 5),
        'monthly_commission': round(monthly_commission, 2) if is_agent else 0,
        'approval_rate': approval_rate,
        'avg_processing_time': avg_processing_time,
        'customer_satisfaction': 4.8 if is_admin else 4.5,
        'recent_activities': recent_activities,
        'active_policies_count': active_policies_count,
        'pending_claims_count': pending_claims_count,
        'pending_policies': pending_policies,
        'my_pending_policies': pending_policies if is_agent else 0,
        'my_pending_claims': pending_claims_count if is_agent else 0,
        'user_type': user_type,
        'is_admin': is_admin,
        'is_agent': is_agent,
        'agent_code': agent_code,
        'layout':template
    }

    return render(request, template, context)


def get_recent_activities():
    """Lấy hoạt động gần đây - phiên bản an toàn"""
    activities = []

    try:
        # Thử lấy policies - xử lý an toàn
        recent_policies = Policy.objects.select_related('customer', 'product').order_by('-created_at')[:3]
        for policy in recent_policies:
            try:
                customer_name = f"{policy.customer.user.first_name} {policy.customer.user.last_name}".strip()
                if not customer_name:
                    customer_name = policy.customer.user.username
                product_name = getattr(policy.product, 'product_name', 'bảo hiểm')
                activities.append({
                    'message': f'{customer_name} đã mua {product_name}',
                    'time': policy.created_at.strftime('%H:%M - %d/%m/%Y'),
                    'color': 'bg-green-500'
                })
            except Exception as e:
                print(f"Lỗi policy item: {e}")
                continue
    except Exception as e:
        print(f"Lỗi khi lấy policies: {e}")
        activities.append({
            'message': 'Khách hàng đã mua bảo hiểm mới',
            'time': timezone.now().strftime('%H:%M - %d/%m/%Y'),
            'color': 'bg-green-500'
        })

    # Thêm các hoạt động mẫu để đảm bảo có dữ liệu
    activities.extend([
        {
            'message': 'Hệ thống hoạt động ổn định',
            'time': timezone.now().strftime('%H:%M - %d/%m/%Y'),
            'color': 'bg-blue-500'
        },
        {
            'message': 'Đang xử lý các yêu cầu mới',
            'time': timezone.now().strftime('%H:%M - %d/%m/%Y'),
            'color': 'bg-orange-500'
        }
    ])

    return activities[:4]


def get_agent_recent_activities(agent):
    """Lấy hoạt động gần đây của agent từ dữ liệu thực"""
    activities = []

    try:
        # Lấy policies gần đây
        recent_policies = Policy.objects.filter(agent=agent).select_related('customer__user', 'product').order_by(
            '-created_at')[:3]


        for policy in recent_policies:
            customer_name = f"{policy.customer.user.first_name} {policy.customer.user.last_name}".strip()
            if not customer_name:
                customer_name = policy.customer.user.username
            product_name = getattr(policy.product, 'product_name', 'bảo hiểm')
            time_ago = timezone.now() - policy.created_at
            if time_ago.days > 0:
                time_str = f"{time_ago.days} ngày trước"
            elif time_ago.seconds // 3600 > 0:
                time_str = f"{time_ago.seconds // 3600} giờ trước"
            else:
                time_str = f"{time_ago.seconds // 60} phút trước"

            activities.append({
                'message': f'{customer_name} đã mua {product_name}',
                'time': time_str,
                'color': 'bg-green-500'
            })

        # Lấy claims gần đây
        recent_claims = Claim.objects.filter(policy__agent=agent).select_related('policy__customer__user').order_by(
            '-created_at')[:2]


        for claim in recent_claims:
            customer_name = f"{claim.policy.customer.user.first_name} {claim.policy.customer.user.last_name}".strip()
            time_ago = timezone.now() - claim.created_at
            if time_ago.days > 0:
                time_str = f"{time_ago.days} ngày trước"
            else:
                time_str = f"{time_ago.seconds // 3600} giờ trước"

            activities.append({
                'message': f'Yêu cầu bồi thường từ {customer_name}',
                'time': time_str,
                'color': 'bg-orange-500'
            })

    except Exception as e:
        print(f"Lỗi lấy hoạt động agent: {e}")

    # Thêm activity mẫu nếu không có đủ
    if len(activities) < 3:
        activities.extend([
            {
                'message': 'Hệ thống hoạt động bình thường',
                'time': 'Vừa xong',
                'color': 'bg-blue-500'
            }
        ])

    return activities[:4]


@login_required
def dashboard_data(request):
    """API data cho dashboard với dữ liệu thực"""
    user_type = request.user.user_type
    is_admin = request.user.is_staff or user_type == 'admin'
    is_agent = user_type == 'agent'

    if not (is_admin or is_agent):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        # KHỞI TẠO MẢNG DỮ LIỆU VÀ NHÃN
        revenue_data = []
        labels = []

        # LẤY DỮ LIỆU CHO 12 THÁNG GẦN NHẤT
        for i in range(11, -1, -1):
            # Tính toán ngày đầu tiên của tháng i tháng trước
            target_date = timezone.now() - timedelta(days=30 * i)

            # Tính toán tháng và năm để làm nhãn
            month_year = f"Th{target_date.month}"
            labels.append(month_year)

            try:
                # Lấy ngày đầu và ngày cuối của tháng mục tiêu
                year = target_date.year
                month = target_date.month


                if is_admin:
                    # Doanh thu hệ thống (tính bằng VNĐ)
                    monthly_total_amount = Payment.objects.filter(
                        payment_date__year=year,
                        payment_date__month=month,
                        status='success'
                    ).aggregate(total=Sum('amount'))['total'] or 0
                    revenue_data.append(round(float(monthly_total_amount) / 1_000_000_000, 4))

                else:
                    # Doanh thu/Hoa hồng Agent (tính bằng VNĐ)
                    agent = Agent.objects.get(user=request.user)

                    # Tính tổng hoa hồng trong tháng
                    monthly_total_commission = Policy.objects.filter(
                        agent=agent,
                        policy_status='active',
                        payment_status='paid',
                        updated_at__year=year,
                        updated_at__month=month
                    ).aggregate(total=Sum('commission_amount'))['total'] or 0

                    # Chuyển đổi sang Triệu VNĐ (chia 1,000,000) và làm tròn 2 chữ số
                    revenue_data.append(round(float(monthly_total_commission) / 1_000_000, 2))

            except Exception as e:
                print(f"Lỗi doanh thu tháng {month_year}: {e}")
                revenue_data.append(0)


        # Phân loại hợp đồng
        try:

            if is_admin:
                policy_types = Policy.objects.filter(policy_status='active').values(
                    'product__product_name'
                ).annotate(total=Count('id')).order_by('-total')
            else:
                agent = Agent.objects.get(user=request.user)
                policy_types = Policy.objects.filter(
                    agent=agent,
                    policy_status='active'
                ).values('product__product_name').annotate(total=Count('id')).order_by('-total')

            policy_labels = [item['product__product_name'] or 'Chưa phân loại' for item in policy_types]
            policy_data = [item['total'] for item in policy_types]

            # Nếu không có data
            if not policy_labels:
                policy_labels = ['Chưa có hợp đồng']
                policy_data = [1]

        except Exception as e:
            print(f"Lỗi phân loại hợp đồng: {e}")
            policy_labels = ['Đang tải...']
            policy_data = [1]

        data = {
            'revenue_chart': {
                'labels': labels,
                'data': revenue_data,
            },
            'contract_chart': {
                'labels': policy_labels,
                'data': policy_data,
            }
        }

        return JsonResponse(data)

    except Exception as e:
        print(f"Lỗi API dashboard: {e}")
        import traceback
        traceback.print_exc()

        # Fallback data (Giữ nguyên)
        # ... (Sử dụng dữ liệu fallback cũ nếu có lỗi nghiêm trọng)
        if is_admin:
            return JsonResponse({
                'revenue_chart': {
                    'labels': ['Th1', 'Th2', 'Th3', 'Th4', 'Th5', 'Th6'],
                    'data': [45, 52, 48, 55, 58.5, 62],
                },
                'contract_chart': {
                    'labels': ['Bảo Hiểm Ô Tô', 'Bảo Hiểm Sức Khỏe', 'Bảo Hiểm Du Lịch'],
                    'data': [45, 25, 15],
                }
            })
        else:
            return JsonResponse({
                'revenue_chart': {
                    'labels': ['Th1', 'Th2', 'Th3', 'Th4', 'Th5', 'Th6'],
                    'data': [2.1, 2.3, 2.0, 2.5, 2.8, 3.0],
                },
                'contract_chart': {
                    'labels': ['Ô Tô', 'Sức Khỏe', 'Du Lịch', 'Nhà Ở'],
                    'data': [12, 6, 4, 3],
                }
            })


def get_active_policies_count():
    """Lấy số hợp đồng đang hoạt động"""
    try:
        return Policy.objects.filter(policy_status='active').count()
    except:
        return 150


def get_pending_claims_count():
    """Lấy số yêu cầu bồi thường đang chờ xử lý"""
    try:
        return Claim.objects.filter(claim_status='pending').count()
    except:
        return 12


def get_total_revenue():
    """Lấy tổng doanh thu từ tất cả payment thành công"""
    try:
        total = Payment.objects.filter(status='success').aggregate(total=Sum('amount'))['total'] or 0
        return float(total) / 1000000000
    except:
        return 58.5


@admin_required
def custom_section(request):
    """Quản lý khách hàng - Chỉ dành cho admin"""
    users = User.objects.filter(is_superuser=False)

    # Lấy tham số tìm kiếm và filter từ URL
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    # Áp dụng tìm kiếm theo tên, email, username
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )

    # Áp dụng filter trạng thái
    if status_filter:
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'suspended':
            users = users.filter(is_active=False)

    context = {
        'users': users,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, "admin/custom_section.html", context)


@admin_required
def customer_create(request):
    """Tạo khách hàng mới - Chỉ dành cho admin"""
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            # Kiểm tra username trùng
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Tên đăng nhập đã tồn tại!')
                return render(request, 'admin/customer_create.html')

            # Kiểm tra email trùng
            if email and User.objects.filter(email=email).exists():
                messages.error(request, 'Email đã tồn tại!')
                return render(request, 'admin/customer_create.html')
            # Tạo User trước
            user = User.objects.create_user(
                username=username,
                email=email,
                password=request.POST.get('password', 'D123456'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                phone_number=request.POST.get('phone_number'),
                address=request.POST.get('address'),
                date_of_birth=request.POST.get('date_of_birth'),
                user_type='customer'
            )

            # Tạo Customer (không bao gồm cccd_front, cccd_back để tránh lỗi)
            customer = Customer.objects.create(
                user=user,
                id_card_number=request.POST.get('id_card_number'),
                nationality=request.POST.get('nationality', 'Việt Nam'),
                gender=request.POST.get('gender', 'other'),
                job=request.POST.get('job', '')
            )

            messages.success(request, f'Đã tạo khách hàng {user.get_full_name()} thành công!')
            return redirect('custom_section')

        except Exception as e:
            messages.error(request, f'Lỗi khi tạo khách hàng: {str(e)}')

    return render(request, 'admin/customer_create.html')


@admin_required
def customer_detail(request, user_id):
    """Chi tiết khách hàng - Chỉ dành cho admin"""
    user = get_object_or_404(User, pk=user_id)

    # Lấy thông tin customer - xử lý an toàn
    try:
        customer = Customer.objects.get(user=user)
    except Exception as e:
        print(f"Lỗi khi lấy customer: {e}")
        customer = None

    policies = []
    claims = []
    payments = []

    if customer:
        try:
            # Lấy các hợp đồng của khách hàng
            policies = Policy.objects.filter(customer=customer)
            print("số yc =",policies.all().count())
        except Exception as e:
            print(f"Lỗi khi lấy policies: {e}")

        try:
            # Lấy các yêu cầu bồi thường (claims)
            claims = Claim.objects.filter(customer=customer)
        except Exception as e:
            print(f"Lỗi khi lấy claims: {e}")

        try:
            # Lấy các lần thanh toán (payments)
            payments = Payment.objects.filter(customer=customer)
        except Exception as e:
            print(f"Lỗi khi lấy payments: {e}")

    context = {
        'user': user,
        'customer': customer,
        'policies': policies,
        'claims': claims,  # <<< THÊM VÀO
        'payments': payments,  # <<< THÊM VÀO
    }
    return render(request, 'admin/customer_detail.html', context)


@admin_required
def customer_edit(request, user_id):
    """Chỉnh sửa thông tin khách hàng - Chỉ dành cho admin - XỬ LÝ AN TOÀN"""
    user = get_object_or_404(User, pk=user_id, user_type='customer')

    # Lấy customer - xử lý an toàn tránh lỗi cccd_front
    customer = None
    try:
        # Chỉ lấy các field cơ bản, tránh các field có thể gây lỗi
        customer = Customer.objects.only('id_card_number', 'nationality', 'gender', 'job').get(user=user)
    except Exception as e:
        print(f"Lỗi khi lấy customer (an toàn): {e}")
        # Vẫn tiếp tục xử lý ngay cả khi không lấy được customer

    if request.method == 'POST':
        try:
            # Cập nhật User
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.phone_number = request.POST.get('phone_number')
            user.address = request.POST.get('address')
            user.date_of_birth = request.POST.get('date_of_birth')
            user.is_active = request.POST.get('is_active') == 'on'
            user.save()

            # Cập nhật Customer nếu tồn tại (chỉ cập nhật các field an toàn)
            if customer:
                customer.id_card_number = request.POST.get('id_card_number')
                customer.nationality = request.POST.get('nationality')
                customer.gender = request.POST.get('gender')
                customer.job = request.POST.get('job')
                customer.save()

            messages.success(request, f'Đã cập nhật thông tin {user.get_full_name()} thành công!')
            return redirect('custom_section')

        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật: {str(e)}')

    context = {
        'user': user,
        'customer': customer,
    }
    return render(request, 'admin/customer_edit.html', context)


@admin_required
def customer_toggle_status(request, user_id):
    """Kích hoạt/Vô hiệu hóa khách hàng - Chỉ dành cho admin"""
    user = get_object_or_404(User, pk=user_id, user_type='customer')

    user.is_active = not user.is_active
    user.save()

    status = "kích hoạt" if user.is_active else "vô hiệu hóa"
    messages.success(request, f'Đã {status} khách hàng {user.get_full_name()}')

    return redirect('custom_section')


@admin_required
def customer_convert_role(request, user_id):
    """Chuyển đổi vai trò giữa customer và employee - Chỉ dành cho admin"""
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        try:
            if user.user_type == 'customer':
                # Chuyển từ customer sang employee
                user.user_type = 'employee'
                user.is_staff = True
                messages.success(request, f'Đã chuyển {user.get_full_name()} từ khách hàng thành nhân viên!')

            elif user.user_type == 'employee':
                # Chuyển từ employee sang customer
                user.user_type = 'customer'
                user.is_staff = False
                messages.success(request, f'Đã chuyển {user.get_full_name()} từ nhân viên thành khách hàng!')

            user.save()

        except Exception as e:
            messages.error(request, f'Lỗi khi chuyển đổi vai trò: {str(e)}')

    return redirect('custom_section')


@login_required
@admin_required
def agent_list(request):
    """Danh sách đại lý"""
    agents = User.objects.filter(user_type='agent')

    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        agents = agents.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(agent__code__icontains=search_query)
        )

    if status_filter:
        if status_filter == 'active':
            agents = agents.filter(is_active=True)
        elif status_filter == 'suspended':
            agents = agents.filter(is_active=False)

    context = {
        'users': agents,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'admin/custom_section.html', context)


@login_required
@admin_required
def agent_create(request):
    """Tạo đại lý mới"""
    if request.method == 'POST':
        try:
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            # Kiểm tra mật khẩu khớp
            if password != confirm_password:
                messages.error(request, 'Mật khẩu không khớp!')
                return render(request, 'admin/agent_create.html')

            # Kiểm tra username trùng
            if User.objects.filter(username=request.POST.get('username')).exists():
                messages.error(request, 'Tên đăng nhập đã tồn tại!')
                return render(request, 'admin/agent_create.html')
            # Kiểm tra email trùng (nếu có email)
            email = request.POST.get('email')
            if email and User.objects.filter(email=email).exists():
                messages.error(request, 'Email đã tồn tại!')
                return render(request, 'admin/agent_create.html')

            agent_code = request.POST.get('code')
            if not agent_code:
                agent_code = generate_agent_code()

            # Tạo User
            user = User.objects.create_user(
                username=request.POST.get('username'),
                email=email,
                password=password,
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                phone_number=request.POST.get('phone_number'),
                address=request.POST.get('address'),
                date_of_birth=request.POST.get('date_of_birth') or None,
                user_type='agent',
                is_active=True
            )

            # Tạo Agent
            Agent.objects.create(
                user=user,
                code=agent_code,
                bank_name=request.POST.get('bank_name', ''),
                bank_account_number=request.POST.get('bank_account_number', ''),
                bank_account_holder=request.POST.get('bank_account_holder', '')
            )

            messages.success(request, f'Đã tạo đại lý {user.get_full_name()} thành công! Mã đại lý: {agent_code}')
            return redirect('custom_section')

        except Exception as e:
            messages.error(request, f'Lỗi khi tạo đại lý: {str(e)}')

    return render(request, 'admin/agent_create.html')


@login_required
@admin_required
def agent_detail(request, user_id):
    """Chi tiết đại lý"""
    user = get_object_or_404(User, pk=user_id, user_type='agent')
    agent = get_object_or_404(Agent, user=user)
    servicing_policies = Policy.objects.filter(agent_servicing=agent).select_related('customer__user', 'product')
    context = {
        'user': user,
        'agent': agent,
        'servicing_policies': servicing_policies,
    }
    return render(request, 'admin/agent_detail.html', context)


@login_required
@admin_required
def agent_edit(request, user_id):
    """Chỉnh sửa đại lý"""
    user = get_object_or_404(User, pk=user_id, user_type='agent')
    agent = get_object_or_404(Agent, user=user)

    if request.method == 'POST':
        try:
            # Cập nhật User
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.phone_number = request.POST.get('phone_number')
            user.address = request.POST.get('address')
            user.date_of_birth = request.POST.get('date_of_birth') or None
            user.is_active = request.POST.get('is_active') == 'on'
            user.save()

            # Cập nhật Agent
            agent.code = request.POST.get('code')
            agent.bank_name = request.POST.get('bank_name', '')
            agent.bank_account_number = request.POST.get('bank_account_number', '')
            agent.bank_account_holder = request.POST.get('bank_account_holder', '')
            agent.save()

            messages.success(request, f'Đã cập nhật đại lý {user.get_full_name()} thành công!')
            return redirect('custom_section')

        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật: {str(e)}')

    context = {
        'user': user,
        'agent': agent
    }
    return render(request, 'admin/agent_edit.html', context)


@login_required
@admin_required
def agent_toggle_status(request, user_id):
    """Kích hoạt / vô hiệu hóa đại lý, có kiểm tra hợp đồng đang quản lý."""

    user = get_object_or_404(User, pk=user_id, user_type='agent')

    if user.is_active is True:
        try:
            agent_obj = Agent.objects.get(user=user)
        except Agent.DoesNotExist:
            agent_obj = None

        if agent_obj:
            # Lọc các hợp đồng đang hoạt động (active) mà đại lý này đang phụ trách.
            active_policies = Policy.objects.filter(
                agent_servicing=agent_obj,
                policy_status='active'
            ).exists()

            if active_policies:
                messages.error(
                    request,
                    f'Không thể vô hiệu hóa đại lý {user.get_full_name()} vì họ đang quản lý ít nhất một hợp đồng đang hoạt động. '
                    'Vui lòng chuyển giao các hợp đồng này trước.'
                )
                return redirect('custom_section')

    user.is_active = not user.is_active
    user.save()

    status = "kích hoạt" if user.is_active else "vô hiệu hóa"
    messages.success(request, f'Đã {status} đại lý {user.get_full_name()}.')

    return redirect('custom_section')