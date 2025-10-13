let currentStep = 1;
let selectedProduct = null;
let personalInfo = {};
let personalInfo_benefic ={}
let final_premium=0;
let selectedPaymentMethod = null;
document.addEventListener('DOMContentLoaded', function() {
    updateStepIndicator();
    populateYearSelects();

    // Nếu có sản phẩm đã chọn từ localStorage thì render lại
    const savedProduct = localStorage.getItem("selectedProduct");
    if (savedProduct) {
        selectedProduct = JSON.parse(savedProduct);
        renderSelectedProduct();
        document.getElementById('continue-step-1').disabled = false;
    }
});

// --- Year Dropdown ---
function populateYearSelects() {
    const currentYear = new Date().getFullYear();
    const carYearSelect = document.getElementById('carYear');
    if (carYearSelect) {
        for (let year = currentYear; year >= currentYear - 20; year--) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            carYearSelect.appendChild(option);
        }
    }
}

// --- Step Navigation ---
function goToStep(step) {
    if (step < currentStep || validateCurrentStep()) {
        document.getElementById(`step-${currentStep}-content`).classList.add('hidden');
        currentStep = step;
        document.getElementById(`step-${currentStep}-content`).classList.remove('hidden');

        updateStepIndicator();
        window.scrollTo({ top: 0, behavior: 'smooth' });

        if (step === 2) {
            renderSelectedProduct();
        }
    }
}

function updateStepIndicator() {
    for (let i = 1; i <= 5; i++) {
        const stepElement = document.getElementById(`step-${i}`);
        if (!stepElement) continue;
        if (i <= currentStep) {
            stepElement.className =
                'step-indicator w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold active';
        } else {
            stepElement.className =
                'step-indicator w-12 h-12 bg-gray-300 rounded-full flex items-center justify-center text-gray-500 font-bold';
        }
    }
}

// --- Select Product ---
function selectProduct(productId) {
    const card = event.currentTarget;
    const name = card.querySelector("h3").innerText;
    const description = card.querySelector("p").innerText;
    const price = card.querySelector(".text-2xl").innerText;

    selectedProduct = { id: productId, name, description, price };

    // Lưu vào localStorage
    localStorage.setItem("selectedProduct", JSON.stringify(selectedProduct));

    // Highlight
    document.querySelectorAll('.product-card').forEach(c => c.classList.remove('border-blue-500'));
    card.classList.add('border-blue-500');
    document.getElementById('continue-step-1').disabled = false;
}

function renderSelectedProduct() {
    const container = document.getElementById("product-summary-step2");
    const productData = selectedProduct || JSON.parse(localStorage.getItem("selectedProduct"));

    if (productData) {
        container.innerHTML = `
            <div class="p-4 border rounded-lg bg-gray-50">
                <h4 class="font-bold text-gray-800">${productData.name}</h4>
                <p class="text-gray-600 text-sm mb-2">${productData.description}</p>
                <p class="text-blue-600 font-semibold">${productData.price}</p>
            </div>
        `;
    } else {
        container.innerHTML = `<p class="text-sm text-gray-500 italic">Chưa có sản phẩm nào được chọn</p>`;
    }
}
// Calculate age from birth date
function calculateAge(birthId, ageId) {
    const birthDate = document.getElementById(birthId).value;
    if (birthDate) {
        const today = new Date();
        const birth = new Date(birthDate);
        let age = today.getFullYear() - birth.getFullYear();
        const monthDiff = today.getMonth() - birth.getMonth();

        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
            age--;
        }

        if (birth > today || age < 0) {
            showPopup("Vui lòng chọn ngày sinh đúng!", "error");
            document.getElementById(ageId).value = "";
            return;
        }

        document.getElementById(ageId).value = age;
    }
}
// Save personal info
function savePersonalInfo(data) {
    personalInfo = {
        fullName: data.personalInfo.fullname,
        birthDate: data.personalInfo.birthDate,
        age:data.personalInfo.age,
        id_card_number:data.personalInfo.id_card_number,
        gender:data.personalInfo.gender,
        occupation:data.personalInfo.occupation,
        phone:data.personalInfo.phone,
        email:data.personalInfo.email,
        address:data.personalInfo.address,
        weight:data.personalInfo.email,
        height:data.personalInfo.height,
        health_conditions:data.personalInfo.health_conditions,
    };
    personalInfo_benefic = {
        fullname:data.personalInfo.fullname_benefic,
        birthDate: data.personalInfo.birthDate_benefic,
        id_card_number: data.personalInfo.id_card_number_benefic,
        relationship_to_customer: data.personalInfo.relationship_to_customer,
    };
}

function showPopup(message, type = "success") {
    // Xóa popup cũ nếu có
    const oldPopup = document.getElementById("popup-message");
    if (oldPopup) oldPopup.remove();

    // Tạo div popup
    const popup = document.createElement("div");
    popup.id = "popup-message";

    // Chọn màu theo loại thông báo
    let bgColor = "bg-blue-500";
    if (type === "success") bgColor = "bg-green-500";
    if (type === "error") bgColor = "bg-red-500";
    if (type === "warning") bgColor = "bg-yellow-500";

    popup.className = `fixed top-5 right-5 z-50 px-4 py-2 text-white rounded shadow-lg ${bgColor} transition-opacity duration-500`;
    popup.textContent = message;

    document.body.appendChild(popup);

    // Debug để chắc chắn hàm chạy
    console.log("Popup hiển thị:", message, "Loại:", type);

    // Sau 2 giây tự động ẩn
    setTimeout(() => {
        popup.style.opacity = "0";
        setTimeout(() => popup.remove(), 500);
    }, 2000);
}


// --- Validation ---
function validateCurrentStep() {
    switch(currentStep) {
        case 1: return selectedProduct !== null;
        case 2: return document.getElementById('health-info-form').checkValidity();
        case 4: return document.querySelector('input[name="payment_method"]:checked') !== null;
        default: return true;
    }
}
async function showInfo() {
    try {
        const res = await fetch('/api/user-info/');
        const data = await res.json();

        // Kiểm tra nếu có dữ liệu trả về hợp lệ
        if (data && Object.keys(data).length > 0) {
            fillInfo(data);
            goToStep(2);
        } else {
            showPopup('Không lấy được thông tin người dùng.');
        }

    } catch (err) {
        console.error('Error:', err);
        showPopup('Vui lòng cập nhật thông tin cá nhân.');
    }
}

function fillInfo(data) {
    age=calculateAge('birthDate','ageDisplay');
    birthInput = document.querySelector('#birthDate');
    ageDisplay = document.querySelector('#ageDisplay');


    document.getElementById("fullName").value = data.full_name || '';
    document.getElementById("ageDisplay").value =age  || '0';
    document.getElementById("birthDate").value = data.birth_date || '';
    document.getElementById("gender").value = data.gender || '';
    document.getElementById("address").value = data.address || '';
    document.getElementById("id_card_number").value = data.id_card_number || '';
    document.getElementById("occupation").value = data.occupation || '';
    document.getElementById("phone").value = data.phone || '';
    document.getElementById("email").value = data.email || '';
}

// --- Backend Interaction ---
function submitToDjangoForCalculation() {
    const form = document.getElementById('health-info-form');
    const formData = new FormData(form);

    // Đảm bảo có product_id nếu nó tồn tại
    if (selectedProduct && selectedProduct.id) {
        formData.append('product_id', selectedProduct.id);
    } else {
        showPopup('Lỗi: Vui lòng chọn một sản phẩm bảo hiểm trước.');
        return;
    }

    showLoading('Đang tính toán phí bảo hiểm...');

    const oldErrors = form.querySelectorAll('.error-message');
    oldErrors.forEach(e => e.remove());

    fetch('/payments/api/calculate-premium/', {
        method: 'POST',
        body: formData
    })
    .then(res => {
        if (!res.ok) {
            return res.json().then(errorData => {
                throw errorData;
            });
        }
        return res.json();
    })
    .then(data => {
        savePersonalInfo(data);
        final_premium = data.final_premium;
        updateFinalOrderSummary(data);
        displayPremiumResults(data);

        setTimeout(() => {
            hideLoading();
            goToStep(3);
        }, 1500);
    })
    .catch(errorData => {
        hideLoading();

        if (errorData && errorData.errors) {
            showPopup('Vui lòng kiểm tra lại các thông tin được đánh dấu đỏ.');
            displayValidationErrors(errorData.errors);
        } else if (errorData && errorData.error) {

            showPopup('Có lỗi xảy ra: ' + errorData.error);
        } else {
            showPopup('Không thể kết nối đến máy chủ. Vui lòng thử lại.');
            console.error('Error:', errorData);
        }
    });
}

function displayValidationErrors(errors) {
    for (const fieldName in errors) {

        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            const errorMessages = errors[fieldName];
            const errorElement = document.createElement('p');
            errorElement.className = 'error-message text-red-500 text-sm mt-1';
            errorElement.textContent = errorMessages.join(' ');

            // Thêm thông báo lỗi vào ngay sau trường input
            field.insertAdjacentElement('afterend', errorElement);
        }
    }
}


function displayPremiumResults(data) {
    document.getElementById('calculated-premium').textContent = formatCurrency(data.final_premium);
    const breakdownContainer = document.getElementById('premium-breakdown');
    breakdownContainer.innerHTML = `
        <div class="space-y-3">
            ${data.breakdown.map(item => `
                <div class="flex justify-between text-sm">
                    <span class="text-gray-600">${item.name}:</span>
                    <span class="font-medium ${item.type === 'discount' ? 'text-green-600' : 'text-gray-800'}">
                        ${item.amount >= 0 ? '+' : ''}${formatCurrency(item.amount)}
                    </span>
                </div>
            `).join('')}
            <div class="border-t pt-3 flex justify-between font-bold">
                <span>Tổng phí bảo hiểm:</span>
                <span class="text-xl text-green-600">${formatCurrency(data.final_premium)}</span>
            </div>
        </div>
    `;
    // Update risk factors
    const factorsContainer = document.getElementById('risk-factors');
    factorsContainer.innerHTML = `
        <h4 class="font-bold text-gray-800 mb-4">Các yếu tố ảnh hưởng đến phí</h4>
        <div class="grid md:grid-cols-2 gap-4">
            ${data.factors.map(factor => `
                <div class="flex items-center p-3 rounded-lg ${factor.type === 'positive' ? 'bg-green-50' : factor.type === 'negative' ? 'bg-red-50' : 'bg-gray-50'}">
                    <div class="w-8 h-8 rounded-full flex items-center justify-center mr-3 ${factor.type === 'positive' ? 'bg-green-100' : factor.type === 'negative' ? 'bg-red-100' : 'bg-gray-100'}">
                        <i class="fas ${factor.type === 'positive' ? 'fa-arrow-down text-green-600' : factor.type === 'negative' ? 'fa-arrow-up text-red-600' : 'fa-minus text-gray-600'} text-sm"></i>
                    </div>
                    <div>
                        <div class="font-semibold text-gray-800 text-sm">${factor.factor}</div>
                        <div class="text-xs text-gray-600">${factor.impact}</div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    // Update coverage details
    const coverageContainer = document.getElementById('coverage-details');
    coverageContainer.innerHTML = `
        <div class="flex items-center text-sm text-gray-700">
            <i class="fas fa-check text-green-500 mr-3"></i>
            <span>${data.product.coverage_details}</span>
        </div>
    `;
    //updateCustomerSummary
    updateCustomerSummary(data)
}
// Update customer summary
function updateCustomerSummary(data) {
    const container = document.getElementById('customer-summary');
    container.innerHTML = `
        <div class="space-y-3 text-sm">
            <div class="flex justify-between">
                <span class="text-gray-600">Họ tên:</span>
                <span class="font-medium">${data.personalInfo.fullname}</span>
            </div>
            <div class="flex justify-between">
                <span class="text-gray-600">Tuổi:</span>
                <span class="font-medium">${personalInfo.age}</span>
            </div>
            <div class="flex justify-between">
                <span class="text-gray-600">Nghề nghiệp:</span>
                <span class="font-medium">${data.personalInfo.occupation}</span>
            </div>
            <div class="flex justify-between">
                <span class="text-gray-600">Điện thoại:</span>
                <span class="font-medium">${data.personalInfo.phone}</span>
            </div>
            <div class="flex justify-between">
                <span class="text-gray-600">Email:</span>
                <span class="font-medium">${data.personalInfo.email}</span>
            </div>
        </div>
    `;
}
// Update final order summary
function updateFinalOrderSummary(data) {
    const container = document.getElementById('final-order-summary');
    container.innerHTML = `
        <div class="space-y-3">
            <div class="flex justify-between text-sm">
                <span class="text-gray-600">Sản phẩm:</span>
                <span class="font-medium">${data.product.product_name}</span>
            </div>
            <div class="flex justify-between text-sm">
                <span class="text-gray-600">Khách hàng:</span>
                <span class="font-medium">${personalInfo.fullName}</span>
            </div>
            <div class="flex justify-between text-sm">
                <span class="text-gray-600">Số điện thoại:</span>
                <span class="font-medium">${personalInfo.phone}</span>
            </div>
            <div class="flex justify-between text-sm">
                <span class="text-gray-600">Mức bảo hiểm:</span>
                <span class="font-medium">${formatCurrency(data.product.max_claim_amount)}</span>
            </div>
            <div class="border-t pt-3 flex justify-between">
                <span class="font-bold text-gray-800">Tổng thanh toán:</span>
                <span class="font-bold text-xl text-green-600">${formatCurrency(final_premium)}</span>
            </div>
        </div>
    `;
}

// Select payment method
function selectPaymentMethod(method) {
    selectedPaymentMethod = method;

    // Update UI
    document.querySelectorAll('.payment-method').forEach(element => {
        element.classList.remove('border-blue-500', 'border-green-500', 'border-purple-500');
        element.classList.add('border-gray-200');
    });

    event.currentTarget.classList.remove('border-gray-200');
    const colors = { card: 'blue', bank: 'green', ewallet: 'purple' };
    event.currentTarget.classList.add(`border-${colors[method]}-500`);

    // Check radio button
    document.querySelector(`input[value="${method}"]`).checked = true;


    // Enable submit button
    document.getElementById('payment-submit').disabled = false;
}

// Show payment form
function showPaymentForm(method) {
    // Hide all forms
    document.querySelectorAll('#bank-form, #ewallet-form').forEach(form => {
        form.classList.add('hidden');
    });

    // Show selected form
    document.getElementById('payment-form').classList.remove('hidden');
    document.getElementById(`${method}-form`).classList.remove('hidden');
}


let paymentDataFromFirstCall = null;
let bankInfoShown = false;

async function processPayment() {
    if (bankInfoShown) {

        const paymentSubmitDiv = document.getElementById("payment-submit");
        paymentSubmitDiv.innerHTML = `
        <p class="font-bold">✅ Cảm ơn bạn, thanh toán đang được xác nhận.</p>
        <button type="button" id="continue-btn" class="btn">Tiếp tục</button>
        `;
        displayContract_Customer(paymentDataFromFirstCall); // Dùng lại data đã lưu

        document.getElementById("continue-btn").addEventListener("click", (event) => {
        event.stopPropagation(); // Ngăn sự kiện lan truyền lên các phần tử cha
        forceGoToStep(5);
        });

        // Reset lại trạng thái
        bankInfoShown = false;
        paymentDataFromFirstCall = null;

        return;
    }

    //  đây là lần bấm đầu tiên.
    if (!selectedPaymentMethod) {
        showPopup('Vui lòng chọn phương thức thanh toán trước khi tiếp tục.');
        return;
    }

    const form = document.getElementById('payment-form');
    const formData = new FormData(form);

    if (selectedProduct && selectedProduct.id) {
        formData.append('product_id', selectedProduct.id);
    } else {
        showPopup("Chưa chọn sản phẩm bảo hiểm!");
        return;
    }

    formData.append('payment_method', selectedPaymentMethod);
    formData.append('final_premium', final_premium);
    formData.append('csrfmiddlewaretoken', getCSRFToken());

    try {
        showLoading('Đang xử lý thanh toán');

        const res = await fetch('/payments/api/process/', {
            method: 'POST',
            body: formData
        });

        const data = await res.json();
        hideLoading();

        if (data.success) {
            paymentDataFromFirstCall = data;

            if (selectedPaymentMethod === 'bank') {
                if (!bankInfoShown) {
                    document.getElementById('payment-form').classList.remove('hidden');
                    document.getElementById('bank-form').classList.remove('hidden');
                    displayBankInfo(data);
                    bankInfoShown = true;
                    showPopup("Vui lòng chuyển khoản theo thông tin hiển thị.");
                    return;
                }
            }
        } else {
            alert('Thanh toán thất bại: ' + (data.error || "Không rõ nguyên nhân"));
        }
    } catch (err) {
        hideLoading();
        console.error('Lỗi FE khi gọi API:', err);
        showPopup("Có lỗi hệ thống khi xử lý thanh toán!");
    }
}
function forceGoToStep(step) {
    document.getElementById(`step-${currentStep}-content`).classList.add('hidden');
    currentStep = step;
    document.getElementById(`step-${currentStep}-content`).classList.remove('hidden');
    updateStepIndicator();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}


function displayBankInfo(data){
    document.getElementById('transfer-amount').innerHTML = (final_premium);
    document.getElementById('transfer-content').innerHTML = data.transfer_content;
}

// Display contract
function displayContract_Customer(data) {
    // Update contract number
    document.getElementById('contract-number').textContent = data.contract.policy_number;

    // Update customer info
    const customerInfoContainer = document.getElementById('contract-customer-info');
    customerInfoContainer.innerHTML = `
        <p><strong>Họ và tên:</strong> ${personalInfo.fullName}</p>
        <p><strong>Ngày sinh:</strong> ${personalInfo.birthDate}</p>
        <p><strong>Giới tính:</strong> ${personalInfo.gender === 'male' ? 'Nam' : 'Nữ'}</p>
        <p><strong>CCCD/CMND:</strong> ${personalInfo.id_card_number}</p>
        <p><strong>Nghề nghiệp:</strong> ${personalInfo.occupation}</p>
        <p><strong>Điện thoại:</strong> ${personalInfo.phone}</p>
        <p><strong>Email:</strong> ${personalInfo.email}</p>
        <p><strong>Địa chỉ:</strong> ${personalInfo.address}</p>
    `;
    // Update info personal_benefic
    const personal_beneficContainer = document.getElementById('contract-personalBenefic-info');
    personal_beneficContainer.innerHTML = `
        <p><strong>Họ và tên:</strong> ${personalInfo_benefic.fullname}</p>
        <p><strong>Ngày sinh:</strong> ${personalInfo_benefic.birthDate}</p>
        <p><strong>CCCD/CMND:</strong> ${personalInfo_benefic.id_card_number}</p>
        <p><strong>Mối quan hệ:</strong> ${getRelationship(personalInfo_benefic.relationship_to_customer)}</p>
    `;
    // Update insurance details
    const insuranceDetailsContainer = document.getElementById('contract-insurance-details');
    insuranceDetailsContainer.innerHTML = `
        <div class="grid md:grid-cols-2 gap-6">
            <div>
                <h4 class="font-bold text-gray-800 mb-2">Thông tin sản phẩm</h4>
                <p><strong>Tên sản phẩm:</strong> ${data.contract.product_name}</p>
                <p><strong>Mô tả:</strong> ${data.contract.description}</p>
                <p><strong>Số hợp đồng:</strong> ${data.contract.policy_number}</p>
                <p><strong>Điều khoản và điều kiện: </strong> ${data.contract.terms_and_conditions}</p>
                <p><strong>Thời hạn:</strong> 12 tháng</p>
            </div>
            <div>
                <h4 class="font-bold text-gray-800 mb-2">Thông tin thanh toán</h4>
                <p><strong>Phí bảo hiểm:</strong> ${formatCurrency(final_premium)}</p>
                <p><strong>Mức bảo hiểm tối đa:</strong> ${formatCurrency(data.contract.max_claim_amount)}</p>
                <p><strong>Phương thức:</strong> Chuyển khoản ngân hàng</p>
                <p><strong>Trạng thái:</strong> <span class="text-green-600 font-semibold">${getPaymentStatusText(data.contract.payment_status)}</span></p>
                <p><strong>Ngày thanh toán:</strong> ${data.contract.payment_date}</p>
            </div>
        </div>
        <div class="mt-6">
            <h4 class="font-bold text-gray-800 mb-2">Quyền lợi bảo hiểm</h4>
            ${data.contract.terms_and_conditions}
        </div>
    `;

    // Update dates
    document.getElementById('contract-start-date').textContent = data.contract.start_date;
    document.getElementById('contract-end-date').textContent = data.contract.end_date;
    document.getElementById('contract-created-date').textContent = data.contract.created_at;

    // Update customer signature
    document.getElementById('customer-signature').textContent = personalInfo.fullName;
}
function getPaymentStatusText(status) {
    const statusMap = {
        'pending': 'Chờ xử lý',
        'failed': 'Thất bại',
        'success': 'Thành công'
    };
    return statusMap[status] || status;
}
function getRelationship(status) {
    const statusMap = {
        'spouse': 'Vợ/Chồng',
        'child': 'Con',
        'parent': 'Cha/Mẹ',
        'sibling': 'Anh/Chị/Em',
        'me': 'Chính mình',
    };
    return statusMap[status] || status;
}
// --- Helpers ---
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN').format(amount) + ' VNĐ';
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function showLoading(message) {
    document.getElementById('loading-title').textContent = message;
    document.getElementById('loadingModal').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingModal').classList.add('hidden');
}
function startOver() {
    // Reset all data
    selectedProduct = null;
    personalInfo = {};
    personal_benefic={};
    final_premium=0;
    selectedPaymentMethod = null;
    // Reset forms
    document.getElementById('health-info-form').reset();

    // Go back to step 1
    goToStep(1);


    // Disable continue button
    document.getElementById('continue-step-1').disabled = true;
}
// Beneficiary checkbox
document.getElementById('sameBeneficiary').addEventListener('change', async (e) => {
    const checked = e.target.checked;
    const nameInput = document.querySelector('input[name="fullname_benefic"]');
    const birthInput = document.querySelector('#birthDate_benefic');
    const ageDisplay = document.querySelector('#ageDisplay_benefic');
    const id_card_number = document.querySelector('#id_card_number_benefic');
    const relationshipSelect = document.getElementById("relationship_to_customer");



    if (checked) {
        try {
            const res = await fetch('/api/user-info/');
            const data = await res.json();
            nameInput.value = data.full_name || '';
            birthInput.value = data.birth_date || '';
            id_card_number.value = data.id_card_number ||'';
            calculateAge('birthDate_benefic', 'ageDisplay_benefic');
        } catch (err) {
            console.error('Lỗi khi lấy user info:', err);
        }
    } else {
        // Reset lại nếu bỏ chọn
        nameInput.value = '';
        birthInput.value = '';
        ageDisplay.value = '';
        id_card_number.value ='';
    }
});

