
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
import uuid

from django.views.decorators.http import require_http_methods, require_POST
import json
from insurance_products.models import InsuranceProduct
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, Http404
from django.contrib import messages

from payments.forms import HealthInfoForm
from payments.models import Payment
from policies.models import Policy, PolicyHolder, HealthInfo
from users.models import Customer, Agent, User


def payments_users(request):
    recent_products_ids = request.session.get("recent_products", [])
    recent_products = InsuranceProduct.objects.filter(id__in=recent_products_ids)
    recent_products = sorted(recent_products, key=lambda x: recent_products_ids.index(x.id))
    return render(request, 'payments/payments_users.html', {'recent_products': recent_products})

def calculate_premium_logic(product, cleaned_data):
    AGE_THRESHOLD = 50
    AGE_SURCHARGE_RATE = 0.20
    SMOKER_SURCHARGE_RATE = 0.12
    ALCOHOL_SURCHARGE_RATE = 0.12
    CONDITION_SURCHARGE_RATE = 0.15
    BMI_LOW_RATE = 0.10
    BMI_OVERWEIGHT_RATE = 0.12
    BMI_OBESE_RATE = 0.15

    # --- Lấy dữ liệu từ cleaned_data ---
    age = cleaned_data.get('age')
    is_smoker = cleaned_data.get('smoker') == 'current'
    uses_alcohol = cleaned_data.get('alcohol') == 'sometimes'
    health_conditions = cleaned_data.get('conditions', [])
    weight = float(cleaned_data.get('weight', 0))
    height = float(cleaned_data.get('height', 0)) / 100

    # --- Bắt đầu tính toán ---
    base_premium = float(product.premium_base_amount)
    surcharges = []
    risk_factors = []

    # Phụ phí tuổi
    if age > AGE_THRESHOLD:
        amount = base_premium * AGE_SURCHARGE_RATE
        surcharges.append({"name": f"Phụ phí tuổi (> {AGE_THRESHOLD})", "amount": amount, "type": "surcharge"})
        risk_factors.append({"factor": f"Tuổi > {AGE_THRESHOLD}", "impact": f"Tăng phí {AGE_SURCHARGE_RATE:.0%}", "type": "negative"})

    # Phụ phí hút thuốc
    if is_smoker:
        amount = base_premium * SMOKER_SURCHARGE_RATE
        surcharges.append({"name": "Phụ phí hút thuốc", "amount": amount, "type": "surcharge"})
        risk_factors.append({"factor": "Hút thuốc", "impact": f"Tăng phí {SMOKER_SURCHARGE_RATE:.0%}", "type": "negative"})

    # Phụ phí rượu bia
    if uses_alcohol:
        amount = base_premium * ALCOHOL_SURCHARGE_RATE
        surcharges.append({"name": "Phụ phí rượu bia", "amount": amount, "type": "surcharge"})
        risk_factors.append({"factor": "Uống rượu bia", "impact": f"Tăng phí {ALCOHOL_SURCHARGE_RATE:.0%}", "type": "negative"})

    # Phụ phí bệnh lý
    for condition in health_conditions:
        amount = base_premium * CONDITION_SURCHARGE_RATE
        surcharges.append({"name": f"Phụ phí bệnh: {condition}", "amount": amount, "type": "surcharge"})
        risk_factors.append({"factor": f"Bệnh lý: {condition}", "impact": f"Tăng phí {CONDITION_SURCHARGE_RATE:.0%}", "type": "negative"})

    # Phụ phí BMI
    if weight > 0 and height > 0:
        bmi = round(weight / (height ** 2), 2)
        if bmi < 18.5:
            amount = base_premium * BMI_LOW_RATE
            surcharges.append({"name": f"Phụ phí BMI thấp ({bmi})", "amount": amount, "type": "surcharge"})
            risk_factors.append({"factor": f"BMI thấp ({bmi})", "impact": f"Tăng {BMI_LOW_RATE:.0%}", "type": "negative"})
        elif 25 <= bmi < 30:
            amount = base_premium * BMI_OVERWEIGHT_RATE
            surcharges.append({"name": f"Phụ phí BMI thừa cân ({bmi})", "amount": amount, "type": "surcharge"})
            risk_factors.append({"factor": f"BMI thừa cân ({bmi})", "impact": f"Tăng {BMI_OVERWEIGHT_RATE:.0%}", "type": "negative"})
        elif bmi >= 30:
            amount = base_premium * BMI_OBESE_RATE
            surcharges.append({"name": f"Phụ phí BMI béo phì ({bmi})", "amount": amount, "type": "surcharge"})
            risk_factors.append({"factor": f"BMI béo phì ({bmi})", "impact": f"Tăng {BMI_OBESE_RATE:.0%}", "type": "negative"})
        else:
            risk_factors.append({"factor": f"BMI bình thường ({bmi})", "impact": "Không ảnh hưởng", "type": "positive"})

    # --- Tổng hợp kết quả ---
    total_surcharge_amount = sum(s['amount'] for s in surcharges)
    final_premium = base_premium + total_surcharge_amount

    breakdown = [{"name": f"Phí cơ bản ({product.product_name})", "amount": base_premium, "type": "base"}] + surcharges

    return {
        "final_premium": round(final_premium, 0),
        "breakdown": breakdown,
        "factors": risk_factors,
        "health_conditions": health_conditions,
    }

def split_fullname(fullname):
    parts = fullname.strip().split()

    if len(parts) == 1:
        return "", parts[0]
    elif len(parts) == 2:
        return parts[0], parts[1]
    else:
        lastname = parts[-1]
        firstname = " ".join(parts[:-1])
        return firstname, lastname

@csrf_exempt
@require_POST
def calculate_premium(request):
    try:
        form = HealthInfoForm(request.POST, request.FILES,user=request.user)
        # Lấy thông tin sản phẩm
        product_id = request.POST.get("product_id")
        try:
            product = InsuranceProduct.objects.get(id=product_id, is_active=True)

        except (InsuranceProduct.DoesNotExist, ValueError, TypeError) as e:

            return JsonResponse({"success": False, "errors": {"product_id": ["Sản phẩm không hợp lệ."]}}, status=400)

        if form.is_valid():
            cleaned_data = form.cleaned_data

            # Gọi hàm logic tính toán
            calculation_result = calculate_premium_logic(product, cleaned_data)

            # Lưu thông tin Customer
            user = request.user if request.user.is_authenticated else None
            if not user:
                print("User not authenticated")
                return JsonResponse({
                    "success": False,
                    "error": "Bạn cần đăng nhập để tính phí bảo hiểm."
                }, status=403)

            with transaction.atomic():
                customer_data = {
                    "id_card_number": cleaned_data.get("id_card_number"),
                    "nationality": cleaned_data.get("nationality", "Việt Nam"),
                    "gender": cleaned_data.get("gender", "other"),
                    "job": cleaned_data.get("occupation", ""),
                }
                if user.user_type == "agent":
                    customer_email = cleaned_data.get("email", "")
                    if not customer_email:
                        return JsonResponse({"success": False, "error": "Đại lý cần cung cấp email khách hàng."})
                    fullname = cleaned_data.get("fullname", "")
                    firstname, lastname = split_fullname(fullname)

                    customer_user = User.objects.filter(email=customer_email).first()

                    if customer_user:

                        if customer_user.user_type != "customer":
                            return JsonResponse({
                                "success": False,
                                "error": "Email này đã tồn tại nhưng không phải tài khoản khách hàng."
                            }, status=400)

                        customer = Customer.objects.filter(user=customer_user).first()
                        if not customer:
                            customer = Customer.objects.create(user=customer_user, **customer_data)
                        policy_owner_user = customer_user
                    else:
                        # Chưa có → tạo mới
                        customer_user = User.objects.create(
                            username=customer_email,
                            email=customer_email,
                            user_type="customer",
                            is_active=True,
                            first_name=firstname,
                            last_name=lastname,
                            date_of_birth=cleaned_data.get("birthDate", ""),
                            phone_number=cleaned_data.get("phone", ""),
                            address=cleaned_data.get("address", ""),
                        )
                        customer = Customer.objects.create(user=customer_user, **customer_data)
                        policy_owner_user = customer_user
                else:
                    customer, created = Customer.objects.get_or_create(
                        user=user,
                        defaults=customer_data
                    )
                    policy_owner_user = user
                if not policy_owner_user:
                    return JsonResponse({"success": False, "error": "Lỗi hệ thống: Không xác định được Chủ hợp đồng."},status=500)
                if request.FILES.get("cccd_front"):
                    if customer.cccd_front:
                        customer.cccd_front.delete(save=False)
                    customer.cccd_front = request.FILES["cccd_front"]

                if request.FILES.get("cccd_back"):
                    if customer.cccd_back:
                        customer.cccd_back.delete(save=False)
                    customer.cccd_back = request.FILES["cccd_back"]

                # Cập nhật thông tin cơ bản customer
                customer.id_card_number = cleaned_data.get("id_card_number")
                customer.nationality = cleaned_data.get("nationality", "Việt Nam")
                customer.gender = cleaned_data.get("gender", "other")
                customer.job = cleaned_data.get("occupation", "")
                customer.save()

                # TẠO POLICY HOLDER TẠM THỜI (DRAFT) - KHÔNG CÓ POLICY ID
                policy_holder = PolicyHolder.objects.create(
                    full_name=cleaned_data.get("fullname_benefic", cleaned_data.get("fullname")),
                    date_of_birth=cleaned_data.get("birthDate_benefic", cleaned_data.get("birthDate")),
                    id_card_number=cleaned_data.get("id_card_number_benefic", cleaned_data.get("id_card_number")),
                    relationship_to_customer=cleaned_data.get("relationship_to_customer",'me'),
                    # policy sẽ được set sau trong process_payment
                )

                # Xử lý file upload cho PolicyHolder
                if request.FILES.get("cccd_front_policyHolder"):
                    if policy_holder.cccd_front:
                        policy_holder.cccd_front.delete(save=False)
                    policy_holder.cccd_front = request.FILES["cccd_front_policyHolder"]

                if request.FILES.get("cccd_back_policyHolder"):
                    if policy_holder.cccd_back:
                        policy_holder.cccd_back.delete(save=False)
                    policy_holder.cccd_back = request.FILES["cccd_back_policyHolder"]

                if request.FILES.get("selfie"):
                    if policy_holder.selfie:
                        policy_holder.selfie.delete(save=False)
                    policy_holder.selfie = request.FILES["selfie"]

                if request.FILES.get("health_certificate"):
                    if policy_holder.health_certificate:
                        policy_holder.health_certificate.delete(save=False)
                    policy_holder.health_certificate = request.FILES["health_certificate"]

                policy_holder.save()

                # TẠO HEALTHINFO LIÊN KẾT VỚI POLICYHOLDER
                health_info = HealthInfo.objects.create(
                    policy_holder=policy_holder,
                    height=cleaned_data.get('height'),
                    weight=cleaned_data.get('weight'),
                    smoker=cleaned_data.get('smoker'),
                    alcohol=cleaned_data.get('alcohol'),
                    conditions=cleaned_data.get('conditions', []),
                )

                # Lưu thông tin vào session để process_payment sử dụng
                request.session['draft_data'] = {
                    'product_id': product_id,
                    'final_premium': calculation_result['final_premium'],
                    'policy_holder_id': policy_holder.id,
                    'health_info_id': health_info.id,
                    'policy_owner_user_id': policy_owner_user.id,
                    'beneficiary_data': {
                        'fullname': cleaned_data.get("beneficiary_fullname"),
                        'birthDate': cleaned_data.get("beneficiary_birthdate"),
                        'id_card_number': cleaned_data.get("beneficiary_id_card"),
                        'relationship_to_customer': cleaned_data.get("beneficiary_relationship"),
                    }
                }
                request.session.modified = True
                serializable_cleaned_data = {}
                for key, value in cleaned_data.items():
                    if not hasattr(value, 'file'):
                        serializable_cleaned_data[key] = value
            # Chuẩn bị response data
            product_data = {
                "id": product.id,
                "product_name": product.product_name,
                "description": product.description,
                "premium_base_amount": float(product.premium_base_amount),
                "max_claim_amount": float(product.max_claim_amount),
                "currency": product.currency,
                "coverage_details": product.coverage_details,
            }

            response_data = {
                "success": True,
                "final_premium": calculation_result['final_premium'],
                "currency": product.currency,
                "breakdown": calculation_result['breakdown'],
                "factors": calculation_result['factors'],
                "product": product_data,
                "healthInfoId": health_info.id,
                "personalInfo": serializable_cleaned_data,
                "session_ready": True,
            }

            print("Returning success response")
            return JsonResponse(response_data)

        else:
            print("Form invalid, errors:", form.errors)
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    except Exception as e:
        print("❌ UNEXPECTED ERROR in calculate_premium:", str(e))
        import traceback
        traceback.print_exc()
        return JsonResponse({
            "success": False,
            "error": f"Lỗi server: {str(e)}"
        }, status=500)

@login_required
@csrf_exempt
def process_payment(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Phương thức không hợp lệ"}, status=405)

    try:
        with transaction.atomic():
            # User hiện tại
            current_user = request.user

            product_id = request.POST.get("product_id")
            amount = request.POST.get("final_premium")
            payment_method = request.POST.get("payment_method")
            agent_code = request.POST.get("agent_code")

            if not product_id or not amount or not payment_method:
                return JsonResponse({"success": False, "error": "Thiếu thông tin thanh toán"}, status=400)


            draft_data = request.session.get('draft_data', {})
            policy_holder_id = draft_data.get('policy_holder_id')

            policy_owner_user_id = draft_data.get('policy_owner_user_id')

            # if not policy_holder_id:
            #     return JsonResponse(
            #         {"success": False, "error": "Không tìm thấy thông tin người được bảo hiểm. Vui lòng tính phí lại."},
            #         status=400)

            product = InsuranceProduct.objects.get(id=product_id)

            if current_user.user_type == 'agent' and policy_owner_user_id:
                policy_owner_user = User.objects.get(pk=policy_owner_user_id)
            else:
                policy_owner_user = current_user

            if not hasattr(policy_owner_user, 'customer'):
                return JsonResponse({"success": False, "error": "User không có Customer Profile hợp lệ."}, status=400)

            policy = create_policy(
                policy_owner_user=policy_owner_user,
                product=product,
                final_premium=amount,
                current_user=current_user,
                code=agent_code
            )
            print("policy_owner_user :",policy_owner_user)
            transaction_id = f"GD-{uuid.uuid4().hex[:10].upper()}"
            payment = Payment.objects.create(
                policy=policy,
                amount=amount,
                payment_method=payment_method,
                transaction_id=transaction_id,
                status="pending",
            )

            # CẬP NHẬT POLICYHOLDER VỚI POLICY
            policy_holder = PolicyHolder.objects.get(id=policy_holder_id)
            policy_holder.policy = policy
            policy_holder.save()

            if 'draft_data' in request.session:
                del request.session['draft_data']

        return JsonResponse({
            "success": True,
            "contract": {
                "id": policy.id,
                "product_name": product.product_name,
                "start_date": policy.start_date.strftime("%Y-%m-%d") if policy.start_date else "",
                "end_date": policy.end_date.strftime("%Y-%m-%d") if policy.end_date else "",
                "created_at": policy.created_at,
                "policy_number": policy.policy_number,
                "status": policy.policy_status,
                "transaction_id": payment.transaction_id,
                "description": product.description,
                "coverage_details": product.coverage_details,
                "terms_and_conditions": product.terms_and_conditions,
                "max_claim_amount": product.max_claim_amount,
                "payment_status": payment.status,
                "payment_date": payment.payment_date,
            },
            "transfer_content": f"{policy.policy_number}-{payment.transaction_id}",
        })
    except User.DoesNotExist:
        return JsonResponse({"success": False, "error": "Không tìm thấy người sở hữu hợp đồng"}, status=404)
    except InsuranceProduct.DoesNotExist:
        return JsonResponse({"success": False, "error": "Sản phẩm không tồn tại"}, status=404)
    except PolicyHolder.DoesNotExist:
        return JsonResponse({"success": False, "error": "Không tìm thấy thông tin người được bảo hiểm"}, status=404)
    except Exception as e:
        print("❌ Lỗi trong process_payment:", e)
        return JsonResponse({"success": False, "error": str(e)})

def create_policy(policy_owner_user, product, final_premium, current_user, code=None):

    customer_owner = policy_owner_user.customer
    agent_servicing = None
    agent_seller = None


    if code:
        try:
            agent_seller = Agent.objects.get(code=code)
        except Agent.DoesNotExist:
            pass

    if not agent_seller and current_user.user_type == 'agent':
        try:
            # Lấy Agent liên kết với người đang thao tác
            agent_seller = Agent.objects.filter(user=current_user).first()
        except Agent.DoesNotExist:
            pass

    if agent_seller:
        agent_servicing = agent_seller
    else:
        try:
            agent_servicing = Agent.objects.get(code='DIRECT_SALES')
        except Agent.DoesNotExist:
            agent_servicing = None

    policy = Policy.objects.create(
        customer=customer_owner,
        product=product,
        policy_number=f"HĐ-{uuid.uuid4().hex[:8].upper()}",
        premium_amount=final_premium,
        payment_status="pending",
        policy_status="pending",
        sum_insured=product.max_claim_amount,
        agent=agent_seller,
        agent_servicing=agent_servicing
    )
    return policy
