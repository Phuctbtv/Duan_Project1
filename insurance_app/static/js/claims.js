
let currentStep = 1;
let selectedPolicy = null;
let uploadedFiles = {};

// Next step với validation và thông báo lỗi
function nextStep() {
    if (!validateCurrentStep()) {
        showStepError();
        return;
    }

    // Ẩn step hiện tại
    document.getElementById(`stepContent${currentStep}`).classList.add('hidden');

    // Cập nhật step indicator
    const currentStepEl = document.getElementById(`step${currentStep}`);
    currentStepEl.classList.remove('active');
    currentStepEl.classList.add('completed');
    currentStepEl.innerHTML = '<i class="fas fa-check"></i>';

    // Cập nhật line
    if (currentStep < 4) {
        document.getElementById(`line${currentStep}`).classList.add('bg-green-500');
        document.getElementById(`line${currentStep}`).classList.remove('bg-gray-200');
    }

    // Chuyển đến step tiếp theo
    currentStep++;

    // Hiển thị step mới
    document.getElementById(`stepContent${currentStep}`).classList.remove('hidden');
    document.getElementById(`stepContent${currentStep}`).classList.add('fade-in');

    // Cập nhật step indicator
//    const nextStepEl = document.getElementById(`step${currentStep}`);
//    nextStepEl.classList.add('active');
//    nextStepEl.classList.remove('bg-gray-200', 'text-gray-600');

    // Cập nhật màu text
    updateStepTexts();

    // Populate summary nếu ở step 4
    if (currentStep === 4) {
        populateSummary();
    }

    // Scroll to top
    window.scrollTo(0, 0);
}

// Hiển thị lỗi cụ thể cho từng step
function showStepError() {
    switch (currentStep) {
        case 2:
            // Kiểm tra trường bắt buộc
            const requiredFields = ['incidentDate', 'treatmentType', 'hospitalName', 'hospital_address', 'description', 'diagnosis', 'totalCost'];
            for (let field of requiredFields) {
                const element = document.getElementById(field);
                if (!element || !element.value.trim()) {
                    let fieldName = getFieldName(field);
                    showPopup(`Vui lòng điền thông tin: ${fieldName}`, 'warning');
                    element.focus();
                    return;
                }
            }

            // Validate số tiền
            const totalCost = parseFloat(document.getElementById('totalCost').value);
            if (isNaN(totalCost) || totalCost <= 0) {
                showPopup('Tổng chi phí phải là số lớn hơn 0', 'warning');
                document.getElementById('totalCost').focus();
                return;
            }

            if (totalCost > 99999999.99) {
                showPopup('Số tiền không được vượt quá 99,999,999 VNĐ', 'warning');
                document.getElementById('totalCost').focus();
                return;
            }

            // Validate số tiền yêu cầu
            const requested_amount = parseFloat(document.getElementById('requested_amount').value);
            if (isNaN(requested_amount) || requested_amount <= 0) {
                showPopup('Số tiền yêu cầu bồi thường phải là số lớn hơn 0', 'warning');
                document.getElementById('requested_amount').focus();
                return;
            }

            if (requested_amount > 99999999.99) {
                showPopup('Số tiền không được vượt quá 99,999,999 VNĐ', 'warning');
                document.getElementById('requested_amount').focus();
                return;
            }
            // Validate ngày xảy ra sự cố
            const incidentDate = new Date(document.getElementById('incidentDate').value);
            const today = new Date();
            today.setHours(23, 59, 59, 999);

            if (incidentDate > today) {
                showPopup('Ngày xảy ra sự cố không được lớn hơn ngày hiện tại', 'warning');
                document.getElementById('incidentDate').focus();
                return;
            }

            // Validate ngày nhập viện
            const admissionDate = document.getElementById('admissionDate').value;
            if (admissionDate) {
                const admission = new Date(admissionDate);
                if (admission > today) {
                    showPopup('Ngày nhập viện không được lớn hơn ngày hiện tại', 'warning');
                    document.getElementById('admissionDate').focus();
                    return;
                }
                if (admission < incidentDate) {
                    showPopup('Ngày nhập viện không được nhỏ hơn ngày xảy ra sự cố', 'warning');
                    document.getElementById('admissionDate').focus();
                    return;
                }
            }

            // Validate ngày xuất viện
            const dischargeDate = document.getElementById('dischargeDate').value;
            if (dischargeDate) {
                const discharge = new Date(dischargeDate);
                if (discharge > today) {
                    showPopup('Ngày xuất viện không được lớn hơn ngày hiện tại', 'warning');
                    document.getElementById('dischargeDate').focus();
                    return;
                }
                if (admissionDate && discharge <= new Date(admissionDate)) {
                    showPopup('Ngày xuất viện phải sau ngày nhập viện', 'warning');
                    document.getElementById('dischargeDate').focus();
                    return;
                }
                if (discharge < incidentDate) {
                    showPopup('Ngày xuất viện không được nhỏ hơn ngày xảy ra sự cố', 'warning');
                    document.getElementById('dischargeDate').focus();
                    return;
                }
            }

            // Validate độ dài text
            const description = document.getElementById('description').value.trim();
            const diagnosis = document.getElementById('diagnosis').value.trim();
            const hospitalName = document.getElementById('hospitalName').value.trim();
            const hospitalAddress = document.getElementById('hospital_address').value.trim();
            const doctorName = document.getElementById('doctorName').value.trim();

            if (description.length < 10) {
                showPopup('Mô tả sự cố phải có ít nhất 10 ký tự', 'warning');
                document.getElementById('description').focus();
                return;
            }

            if (diagnosis.length < 5) {
                showPopup('Chẩn đoán phải có ít nhất 5 ký tự', 'warning');
                document.getElementById('diagnosis').focus();
                return;
            }

            if (hospitalName.length < 3) {
                showPopup('Tên bệnh viện phải có ít nhất 3 ký tự', 'warning');
                document.getElementById('hospitalName').focus();
                return;
            }

            if (hospitalAddress.length < 5) {
                showPopup('Địa chỉ bệnh viện phải có ít nhất 5 ký tự', 'warning');
                document.getElementById('hospital_address').focus();
                return;
            }

            if (doctorName && doctorName.length < 3) {
                showPopup('Tên bác sĩ phải có ít nhất 3 ký tự', 'warning');
                document.getElementById('doctorName').focus();
                return;
            }

            break;

        case 3:
            if (!uploadedFiles.medicalBill || uploadedFiles.medicalBill.length === 0) {
                showPopup('Vui lòng tải lên hóa đơn viện phí', 'warning');
                return;
            }
            if (!uploadedFiles.medicalRecords || uploadedFiles.medicalRecords.length === 0) {
                showPopup('Vui lòng tải lên hồ sơ bệnh án', 'warning');
                return;
            }
            break;

        case 4: {
            const requiredCheckboxes = ['agreeTerms', 'agreeProcess', 'agreeContact'];
            const requiredFields = ['accountHolderName', 'accountNumber', 'bankName'];

            const missingFields = requiredFields.filter(id => !document.getElementById(id)?.value.trim());
            const uncheckedBoxes = requiredCheckboxes.filter(id => !document.getElementById(id)?.checked);

            if (missingFields.length) {
                return showPopup('Vui lòng điền đầy đủ thông tin nhận tiền', 'warning');
            }
            if (uncheckedBoxes.length) {
                return showPopup('Vui lòng đồng ý với tất cả điều khoản và cam kết', 'warning');
            }
            break;
        }
    }
}

// Hàm helper để lấy tên trường
function getFieldName(fieldId) {
    const fieldNames = {
        'incidentDate': 'Ngày xảy ra sự cố',
        'treatmentType': 'Loại điều trị',
        'hospitalName': 'Tên bệnh viện',
        'hospital_address': 'Địa chỉ bệnh viện',
        'description': 'Mô tả sự cố',
        'diagnosis': 'Chẩn đoán',
        'totalCost': 'Tổng chi phí',
        'requested_amount': 'Số tiền yêu cầu bồi thường',
        'admissionDate': 'Ngày nhập viện',
        'dischargeDate': 'Ngày xuất viện',
        'doctorName': 'Tên bác sĩ'
    };
    return fieldNames[fieldId] || fieldId;
}

// Previous step
function prevStep() {
    if (currentStep <= 1) return;

    // Hide current step
    document.getElementById(`stepContent${currentStep}`).classList.add('hidden');

    // Update step indicator
    const currentStepEl = document.getElementById(`step${currentStep}`);
    currentStepEl.classList.remove('active');
    currentStepEl.classList.add('bg-gray-200', 'text-gray-600');
    currentStepEl.textContent = currentStep;

    // Move to previous step
    currentStep--;

    // Show previous step
    document.getElementById(`stepContent${currentStep}`).classList.remove('hidden');

    // Update step indicator
    const prevStepEl = document.getElementById(`step${currentStep}`);
    prevStepEl.classList.remove('completed');
    prevStepEl.classList.add('active');
    prevStepEl.textContent = currentStep;

    // Update line
    if (currentStep < 4) {
        document.getElementById(`line${currentStep}`).classList.remove('bg-green-500');
        document.getElementById(`line${currentStep}`).classList.add('bg-gray-200');
    }

    // Update step text colors
    updateStepTexts();

    // Scroll to top
    window.scrollTo(0, 0);
}

// Update step text colors
function updateStepTexts() {
    for (let i = 1; i <= 4; i++) {
        const stepEl = document.getElementById(`step${i}`);
        const textEl = stepEl.nextElementSibling;

        if (stepEl.classList.contains('active')) {
            textEl.classList.remove('text-gray-500');
            textEl.classList.add('text-blue-600', 'font-semibold');
        } else if (stepEl.classList.contains('completed')) {
            textEl.classList.remove('text-gray-500');
            textEl.classList.add('text-green-600', 'font-semibold');
        } else {
            textEl.classList.add('text-gray-500');
            textEl.classList.remove('text-blue-600', 'text-green-600', 'font-semibold');
        }
    }
}

// Validate current step
function validateCurrentStep() {
    switch (currentStep) {
        case 1:
            return true;

        case 2:
        // Kiểm tra các trường bắt buộc có giá trị
            const requiredFields = ['incidentDate', 'treatmentType', 'hospitalName', 'hospital_address', 'description', 'diagnosis', 'totalCost','requested_amount'];
            for (let field of requiredFields) {
                const element = document.getElementById(field);
                if (!element || !element.value.trim()) {
                    return false;
                }
            }

            // Kiểm tra số tiền
            const totalCost = parseFloat(document.getElementById('totalCost').value);
            if (isNaN(totalCost) || totalCost <= 0 || totalCost > 99999999.99) {
                return false;
            }

            // Kiểm tra ngày xảy ra sự cố không lớn hơn hôm nay
            const incidentDate = new Date(document.getElementById('incidentDate').value);
            const today = new Date();
            today.setHours(23, 59, 59, 999);
            if (incidentDate > today) {
                return false;
            }

            // Kiểm tra ngày nhập viện (nếu có)
            const admissionDate = document.getElementById('admissionDate').value;
            if (admissionDate) {
                const admission = new Date(admissionDate);
                if (admission > today || admission < incidentDate) {
                    return false;
                }
            }

            // Kiểm tra ngày xuất viện (nếu có)
            const dischargeDate = document.getElementById('dischargeDate').value;
            if (dischargeDate) {
                const discharge = new Date(dischargeDate);
                if (discharge > today ||
                    (admissionDate && discharge <= new Date(admissionDate)) ||
                    discharge < incidentDate) {
                    return false;
                }
            }

            // Kiểm tra độ dài text
            const description = document.getElementById('description').value.trim();
            const diagnosis = document.getElementById('diagnosis').value.trim();
            const hospitalName = document.getElementById('hospitalName').value.trim();
            const hospitalAddress = document.getElementById('hospital_address').value.trim();
            const doctorName = document.getElementById('doctorName').value.trim();

            if (description.length < 10 ||
                diagnosis.length < 5 ||
                hospitalName.length < 3 ||
                hospitalAddress.length < 5 ||
                (doctorName && doctorName.length < 3)) {
                return false;
            }

            return true;

        case 3:
            // Chỉ kiểm tra file bắt buộc
            return uploadedFiles.medicalBill && uploadedFiles.medicalBill.length > 0 &&
                   uploadedFiles.medicalRecords && uploadedFiles.medicalRecords.length > 0;

        case 4:

            const requiredField = ['bankName','accountNumber','accountHolderName'];
            for (let field of requiredField) {
                const element = document.getElementById(field);
                if (!element || !element.value.trim()) {
                    return false;
                }
            }
            return document.getElementById('agreeTerms').checked &&
                   document.getElementById('agreeProcess').checked &&
                   document.getElementById('agreeContact').checked;

        default:
            return true;
    }
}
// Real-time validation cho các trường
document.addEventListener('DOMContentLoaded', function() {
    let currentPopupTimer = null;

    // Validate ngày xảy ra sự cố
    const incidentDateInput = document.getElementById('incidentDate');
    if (incidentDateInput) {
        incidentDateInput.addEventListener('change', function() {
            const selectedDate = new Date(this.value);
            const today = new Date();

            if (selectedDate > today) {
                this.classList.add('border-red-500', 'bg-red-50');
                if (currentPopupTimer) clearTimeout(currentPopupTimer);
                showPopup('Ngày xảy ra sự cố không được lớn hơn hôm nay', 'warning', true, 3000);
            } else {
                this.classList.remove('border-red-500', 'bg-red-50');
            }
        });
    }

    // Validate ngày nhập viện
    const admissionDateInput = document.getElementById('admissionDate');
    if (admissionDateInput) {
        admissionDateInput.addEventListener('change', function() {
            const admissionDate = new Date(this.value);
            const incidentDate = new Date(document.getElementById('incidentDate').value);
            const today = new Date();

            let hasError = false;
            if (this.value && admissionDate > today) {
                this.classList.add('border-red-500', 'bg-red-50');
                showPopup('Ngày nhập viện không được lớn hơn hôm nay', 'warning', true, 3000);
                hasError = true;
            } else if (this.value && incidentDate && admissionDate < incidentDate) {
                this.classList.add('border-red-500', 'bg-red-50');
                showPopup('Ngày nhập viện không được nhỏ hơn ngày xảy ra sự cố', 'warning', true, 3000);
                hasError = true;
            } else {
                this.classList.remove('border-red-500', 'bg-red-50');
            }


        });
    }

    // Validate ngày xuất viện
    const dischargeDateInput = document.getElementById('dischargeDate');
    if (dischargeDateInput) {
        dischargeDateInput.addEventListener('change', function() {
            const dischargeDate = new Date(this.value);
            const admissionDateValue = document.getElementById('admissionDate').value;
            const admissionDate = admissionDateValue ? new Date(admissionDateValue) : null;
            const incidentDate = new Date(document.getElementById('incidentDate').value);
            const today = new Date();

            let hasError = false;
            if (this.value && dischargeDate > today) {
                this.classList.add('border-red-500', 'bg-red-50');
                showPopup('Ngày xuất viện không được lớn hơn hôm nay', 'warning', true, 3000);
                hasError = true;
            } else if (this.value && admissionDate && dischargeDate <= admissionDate) {
                this.classList.add('border-red-500', 'bg-red-50');
                showPopup('Ngày xuất viện phải sau ngày nhập viện', 'warning', true, 3000);
                hasError = true;
            } else if (this.value && dischargeDate < incidentDate) {
                this.classList.add('border-red-500', 'bg-red-50');
                showPopup('Ngày xuất viện không được nhỏ hơn ngày xảy ra sự cố', 'warning', true, 3000);
                hasError = true;
            } else {
                this.classList.remove('border-red-500', 'bg-red-50');
            }


        });
    }

    // Validate độ dài mô tả
    const descriptionInput = document.getElementById('description');
    if (descriptionInput) {
        descriptionInput.addEventListener('input', debounce(function() {
            const value = this.value.trim();
            if (value.length > 0 && value.length < 10) {
                this.classList.add('border-yellow-500', 'bg-yellow-50');
                showPopup('Mô tả sự cố phải có ít nhất 10 ký tự', 'warning', true, 3000);
            } else if (value.length >= 10) {
                this.classList.remove('border-yellow-500', 'bg-yellow-50');
                this.classList.add('border-green-500', 'bg-green-50');
            } else {
                this.classList.remove('border-yellow-500', 'bg-yellow-50', 'border-green-500', 'bg-green-50');
            }

        }, 800));
    }

    // Validate độ dài chẩn đoán
    const diagnosisInput = document.getElementById('diagnosis');
    if (diagnosisInput) {
        diagnosisInput.addEventListener('input', debounce(function() {
            const value = this.value.trim();
            if (value.length > 0 && value.length < 5) {
                this.classList.add('border-yellow-500', 'bg-yellow-50');
                showPopup('Chẩn đoán phải có ít nhất 5 ký tự', 'warning', true, 3000);
            } else if (value.length >= 5) {
                this.classList.remove('border-yellow-500', 'bg-yellow-50');
                this.classList.add('border-green-500', 'bg-green-50');
            } else {
                this.classList.remove('border-yellow-500', 'bg-yellow-50', 'border-green-500', 'bg-green-50');
            }

        }, 800));
    }

    // Validate tên bệnh viện
    const hospitalNameInput = document.getElementById('hospitalName');
    if (hospitalNameInput) {
        hospitalNameInput.addEventListener('input', debounce(function() {
            const value = this.value.trim();
            if (value.length > 0 && value.length < 3) {
                this.classList.add('border-yellow-500', 'bg-yellow-50');
                showPopup('Tên bệnh viện phải có ít nhất 3 ký tự', 'warning', true, 3000);
            } else if (value.length >= 3) {
                this.classList.remove('border-yellow-500', 'bg-yellow-50');
                this.classList.add('border-green-500', 'bg-green-50');
            } else {
                this.classList.remove('border-yellow-500', 'bg-yellow-50', 'border-green-500', 'bg-green-50');
            }

        }, 800));
    }

    // Validate địa chỉ bệnh viện
    const hospitalAddressInput = document.getElementById('hospital_address');
    if (hospitalAddressInput) {
        hospitalAddressInput.addEventListener('input', debounce(function() {
            const value = this.value.trim();
            if (value.length > 0 && value.length < 5) {
                this.classList.add('border-yellow-500', 'bg-yellow-50');
                showPopup('Địa chỉ bệnh viện phải có ít nhất 5 ký tự', 'warning', true, 3000);
            } else if (value.length >= 5) {
                this.classList.remove('border-yellow-500', 'bg-yellow-50');
                this.classList.add('border-green-500', 'bg-green-50');
            } else {
                this.classList.remove('border-yellow-500', 'bg-yellow-50', 'border-green-500', 'bg-green-50');
            }

        }, 800));
    }

    // Validate tên bác sĩ
    const doctorNameInput = document.getElementById('doctorName');
    if (doctorNameInput) {
        doctorNameInput.addEventListener('input', debounce(function() {
            const value = this.value.trim();
            if (value.length > 0 && value.length < 3) {
                this.classList.add('border-yellow-500', 'bg-yellow-50');
                showPopup('Tên bác sĩ phải có ít nhất 3 ký tự', 'warning', true, 3000);
            } else if (value.length >= 3) {
                this.classList.remove('border-yellow-500', 'bg-yellow-50');
                this.classList.add('border-green-500', 'bg-green-50');
            } else {
                this.classList.remove('border-yellow-500', 'bg-yellow-50', 'border-green-500', 'bg-green-50');
            }

        }, 800));
    }

    // Validate số tiền
    const totalCostInput = document.getElementById('totalCost');
    if (totalCostInput) {
        totalCostInput.addEventListener('input', debounce(function() {
            const value = this.value.trim();
            const amount = parseFloat(value);

            if (value && (isNaN(amount) || amount <= 0)) {
                this.classList.add('border-red-500', 'bg-red-50');
                showPopup('Tổng chi phí phải là số lớn hơn 0', 'warning', true, 3000);
            } else if (value && amount > 99999999.99) {
                this.classList.add('border-red-500', 'bg-red-50');
                showPopup('Số tiền không được vượt quá 99,999,999 VNĐ', 'warning', true, 3000);
            } else if (value && amount > 0) {
                this.classList.remove('border-red-500', 'bg-red-50');
                this.classList.add('border-green-500', 'bg-green-50');
            } else {
                this.classList.remove('border-red-500', 'bg-red-50', 'border-green-500', 'bg-green-50');
            }

        }, 800));
    }
});

// Thêm hàm debounce để tránh validation quá nhiều
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const context = this;
        const later = () => {
            clearTimeout(timeout);
            func.apply(context, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Handle file upload
function handleFileUpload(input, listId) {
    const files = Array.from(input.files);
    const listContainer = document.getElementById(listId);

    files.forEach(file => {
        if (file.size > 10 * 1024 * 1024) {
            showPopup(`File ${file.name} quá lớn. Vui lòng chọn file nhỏ hơn 10MB.`);
            return;
        }

        const fileItem = document.createElement('div');
        fileItem.className = 'uploaded-file flex items-center justify-between p-3 bg-gray-50 rounded-lg';
        fileItem.innerHTML = `
            <div class="flex items-center space-x-3">
                <i class="fas fa-file-alt text-blue-600"></i>
                <div>
                    <p class="font-semibold text-gray-800">${file.name}</p>
                    <p class="text-sm text-gray-600">${formatFileSize(file.size)}</p>
                </div>
            </div>
            <button type="button" onclick="removeFile(this, '${input.id}')" class="text-red-600 hover:text-red-800">
                <i class="fas fa-times"></i>
            </button>
        `;

        listContainer.appendChild(fileItem);
    });

    // Store files
    const fieldName = input.id;
    if (!uploadedFiles[fieldName]) {
        uploadedFiles[fieldName] = [];
    }
    uploadedFiles[fieldName] = uploadedFiles[fieldName].concat(files);


}

// Cập nhật hàm remove file
function removeFile(button, fieldName) {
    const fileName = button.parentElement.querySelector('.font-semibold').textContent;

    // Remove from uploadedFiles
    if (uploadedFiles[fieldName]) {
        uploadedFiles[fieldName] = uploadedFiles[fieldName].filter(file => file.name !== fileName);
    }

    button.parentElement.remove();

}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Submit claim
function submitClaim() {
    if (!validateCurrentStep()) {
        showPopup('Vui lòng kiểm tra lại thông tin trước khi gửi', 'warning');
        return;
    }

    // Lấy policy_id từ data attribute
    const submitBtn = document.getElementById('submitClaim');
    const policyId = submitBtn.getAttribute('data-policy-id');

    if (!policyId) {
        showPopup('Lỗi: Không tìm thấy thông tin hợp đồng', 'error');
        return;
    }

    // Hiển thị loading
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Đang gửi...';
    submitBtn.disabled = true;

    try {
        // Tạo FormData
        const formData = new FormData();

        // Thêm thông tin cơ bản
        const formFields = [
            'incidentDate', 'treatmentType', 'hospitalName', 'hospital_address',
            'doctorName', 'description', 'diagnosis', 'admissionDate',
            'dischargeDate', 'totalCost','requested_amount','bankName','accountNumber','accountHolderName'
        ];

        formFields.forEach(field => {
            const element = document.getElementById(field);
            if (element) {
                formData.append(field, element.value || '');
            }
        });

        // Thêm files
        Object.keys(uploadedFiles).forEach(fieldName => {
            if (uploadedFiles[fieldName] && uploadedFiles[fieldName].length > 0) {
                uploadedFiles[fieldName].forEach(file => {
                    if (file.size > 10 * 1024 * 1024) {
                        throw new Error(`File ${file.name} vượt quá kích thước cho phép (10MB)`);
                    }
                    formData.append(fieldName, file);
                });
            }
        });

        // Gửi AJAX request
        fetch(`/custom_claims/create_claims/${policyId}/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                document.getElementById('claim_number').textContent = data.claim_number;
                document.getElementById('successModal').classList.remove('hidden');
                // Cập nhật link xem chi tiết
                const detailLink = document.getElementById('viewClaimDetail');

                document.body.style.overflow = 'hidden';
            } else {
                showPopup('Lỗi: ' + (data.message || 'Không thể gửi yêu cầu'), 'error');
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            let errorMessage = 'Có lỗi xảy ra khi gửi yêu cầu';

            if (error.message.includes('Failed to fetch')) {
                errorMessage = 'Lỗi kết nối. Vui lòng kiểm tra internet và thử lại.';
            } else if (error.message.includes('HTTP error')) {
                errorMessage = 'Lỗi máy chủ. Vui lòng thử lại sau.';
            }

            showPopup(errorMessage, 'error');
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        });

    } catch (error) {
        showPopup(error.message, 'error');
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}
// Hàm lấy CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
// Modal functions

function populateSummary() {
    const incidentDate = document.getElementById('incidentDate').value;
    const treatmentType = document.getElementById('treatmentType');
    const hospitalName = document.getElementById('hospitalName').value;
    const diagnosis = document.getElementById('diagnosis').value;
    const totalCost = document.getElementById('totalCost').value;

    // Mapping loại điều trị
    const treatmentTypeMap = {
        'outpatient': 'Ngoại trú',
        'inpatient': 'Nội trú',
        'surgery': 'Phẫu thuật',
        'death': 'Tử vong',
        'other': 'Khác'
    };
    // Ngày xảy ra sự cố
    document.getElementById('summaryIncidentDate').textContent =
        incidentDate ? formatDate(incidentDate) : '-';

    // Loại điều trị
    const selectedTreatment = treatmentType.options[treatmentType.selectedIndex];
    document.getElementById('summaryTreatmentType').textContent =
        selectedTreatment.textContent || '-';

    // Bệnh viện
    document.getElementById('summaryHospital').textContent =
        hospitalName || '-';

    // Chẩn đoán
    document.getElementById('summaryDiagnosis').textContent =
        diagnosis || '-';

    // Tổng chi phí
    document.getElementById('summaryTotalCost').textContent =
        totalCost ? formatCurrency(totalCost) : '-';

    // Số tài liệu đã tải
    const totalDocs = Object.values(uploadedFiles).reduce((sum, files) => sum + files.length, 0);
    document.getElementById('summaryDocuments').textContent =
        `${totalDocs} tài liệu`;


}
// Hiển thị popup với message
function showPopup(message, type = 'info', autoClose = false, duration = 1500) {
    // Tạo popup element nếu chưa tồn tại
    let popup = document.getElementById('customPopup');

    if (!popup) {
        popup = document.createElement('div');
        popup.id = 'customPopup';
        popup.className = 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 hidden';
        popup.innerHTML = `
            <div class="bg-white rounded-xl shadow-2xl max-w-md w-full transform transition-all duration-300 scale-95">
                ${autoClose ? '<div id="popupProgress" class="popup-progress rounded-t-xl"></div>' : ''}
                <div class="p-6">
                    <div class="text-center">
                        <div id="popupIcon" class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                            <i class="fas fa-info-circle text-2xl"></i>
                        </div>
                        <h3 id="popupTitle" class="text-xl font-bold mb-2">Thông báo</h3>
                        <p id="popupMessage" class="text-gray-600 mb-6"></p>
                        <button onclick="closePopup()" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                            Đóng
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(popup);
    }

    // Cập nhật nội dung và style theo type
    const popupMessage = document.getElementById('popupMessage');
    const popupIcon = document.getElementById('popupIcon');
    const popupTitle = document.getElementById('popupTitle');

    popupMessage.textContent = message;

    // Thiết lập style theo type
    switch (type) {
        case 'success':
            popupIcon.className = 'w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4';
            popupIcon.innerHTML = '<i class="fas fa-check-circle text-green-600 text-2xl"></i>';
            popupTitle.textContent = 'Thành công!';
            popupTitle.className = 'text-xl font-bold mb-2 text-green-800';
            break;

        case 'error':
            popupIcon.className = 'w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4';
            popupIcon.innerHTML = '<i class="fas fa-exclamation-circle text-red-600 text-2xl"></i>';
            popupTitle.textContent = 'Lỗi!';
            popupTitle.className = 'text-xl font-bold mb-2 text-red-800';
            break;

        case 'warning':
            popupIcon.className = 'w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4';
            popupIcon.innerHTML = '<i class="fas fa-exclamation-triangle text-yellow-600 text-2xl"></i>';
            popupTitle.textContent = 'Cảnh báo';
            popupTitle.className = 'text-xl font-bold mb-2 text-yellow-800';
            break;

        default:
            popupIcon.className = 'w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4';
            popupIcon.innerHTML = '<i class="fas fa-info-circle text-blue-600 text-2xl"></i>';
            popupTitle.textContent = 'Thông báo';
            popupTitle.className = 'text-xl font-bold mb-2 text-blue-800';
    }

    // Hiển thị popup với animation
    popup.classList.remove('hidden');
    setTimeout(() => {
        const popupContent = popup.querySelector('.transform');
        if (popupContent) {
            popupContent.classList.remove('scale-95');
            popupContent.classList.add('scale-100');
        }
    }, 10);

    // Disable scroll body
    document.body.style.overflow = 'hidden';

    // Auto close nếu được kích hoạt
    if (autoClose) {
        setTimeout(() => {
            closePopup();
        }, duration);
    }
}

// Đóng popup
function closePopup() {
    const popup = document.getElementById('customPopup');
    if (popup) {
        popup.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}

function goBack() {
        window.history.back();
}

// Helper functions
function formatDate(dateString) {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('vi-VN');
}

function formatCurrency(amount) {
    if (!amount) return '0 VNĐ';
    return new Intl.NumberFormat('vi-VN', {
        style: 'decimal',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount) + ' VNĐ';
}

// Drag and drop functionality
document.addEventListener('DOMContentLoaded', function() {
    const uploadAreas = document.querySelectorAll('.file-upload-area');

    uploadAreas.forEach(area => {
        area.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });

        area.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
        });

        area.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');

            const files = e.dataTransfer.files;
            const input = this.querySelector('input[type="file"]');

            // Create a new FileList
            const dt = new DataTransfer();
            for (let file of files) {
                dt.items.add(file);
            }
            input.files = dt.files;

            // Trigger change event
            input.dispatchEvent(new Event('change'));
        });
    });
});
