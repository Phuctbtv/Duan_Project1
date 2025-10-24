
    const detailModal = document.getElementById('policyDetailModal');
    const closeDetailModal = document.getElementById('closeDetailModal');
    const closeDetailModalBtn = document.getElementById('closeDetailModalBtn');
    const approvePolicyBtn = document.getElementById('approvePolicyBtn');
    const rejectPolicyBtn = document.getElementById('rejectPolicyBtn');

    // Mapping cho các lựa chọn
    const genderMapping = {
        'male': 'Nam',
        'female': 'Nữ',
        'other': 'Khác'
    };

    const smokingMapping = {
        'never': 'Không hút',
        'former': 'Đã bỏ',
        'current': 'Đang hút'
    };

    const alcoholMapping = {
        'no': 'Không',
        'sometimes': 'Thỉnh thoảng'
    };

    const statusMapping = {
        'pending': { text: 'Chờ duyệt', class: 'bg-orange-100 text-orange-800' },
        'active': { text: 'Đang hoạt động', class: 'bg-green-100 text-green-800' },
        'cancelled': { text: 'Đã hủy', class: 'bg-red-100 text-red-800' }
    };
    // Biến toàn cục để lưu policy ID hiện tại
    let currentPolicyId = null;
    // Hàm hiển thị modal chi tiết
    function showPolicyDetail(policyId) {
        currentPolicyId = policyId;
        // Hiển thị loading
        const detailModal = document.getElementById('policyDetailModal');
        detailModal.classList.remove('hidden');

        // Hiển thị loading state
        document.getElementById('detailPolicyNumber').textContent = 'Đang tải...';
        document.getElementById('detailProductName').textContent = 'Đang tải...';

        // Gọi API để lấy chi tiết hợp đồng
        fetch(`/custom_policies/api/${policyId}/detail/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    populateModal(data.policy);
                } else {
                    alert('Có lỗi xảy ra khi tải thông tin hợp đồng: ' + data.error);
                    closeModal();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Có lỗi xảy ra khi tải thông tin hợp đồng');
                closeModal();
            });
    };
    // ========== MODAL DUYỆT HỢP ĐỒNG ==========
    function showApprovalModal(policyId) {
        currentPolicyId = policyId;
        document.getElementById('approvalModal').classList.remove('hidden');
        document.getElementById('approvalNote').value = '';
    }
    function closeApprovalModal() {
        document.getElementById('approvalModal').classList.add('hidden');
    }
    function confirmApproval() {
        const note = document.getElementById('approvalNote').value;

        if (!confirm('Bạn có chắc chắn muốn duyệt hợp đồng này?')) {
            return;
        }

        // Gửi request duyệt hợp đồng
        fetch(`/custom_policies/api/${currentPolicyId}/approve/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                note: note
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
               location.reload();
            } else {
                alert('Lỗi: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);

        })
        .finally(() => {
            closeApprovalModal();
        });
    }

    // ========== MODAL TỪ CHỐI HỢP ĐỒNG ==========
    function showRejectionModal(policyId) {
        currentPolicyId = policyId;
        document.getElementById('rejectionModal').classList.remove('hidden');
        document.getElementById('rejectionReason').value = '';
    }

    function closeRejectionModal() {
        document.getElementById('rejectionModal').classList.add('hidden');
    }

    function confirmRejection() {
        const reason = document.getElementById('rejectionReason').value;

        if (!reason.trim()) {
            showPopup('Vui lòng nhập lý do từ chối');
            return;
        }

        if (!confirm('Bạn có chắc chắn muốn từ chối hợp đồng này?')) {
            return;
        }

        // Gửi request từ chối hợp đồng
        fetch(`/custom_policies/api/${currentPolicyId}/reject/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                reason: reason
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                showPopup('Lỗi: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        })
        .finally(() => {
            closeRejectionModal();
        });
    }

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    // Đóng modal khi click outside
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-backdrop')) {
            closeDetailModal();
            closeApprovalModal();
            closeRejectionModal();
        }
    });
    // Hàm điền dữ liệu vào modal
    function populateModal(policy) {
        // Thông tin hợp đồng
        document.getElementById('detailPolicyNumber').textContent = policy.policy_number;
        document.getElementById('detailProductName').textContent = policy.product.product_name;
        document.getElementById('detailPremium').textContent = formatCurrency(policy.premium_amount);
        document.getElementById('detailStartDate').textContent = policy.start_date ? formatDate(policy.start_date) : 'Chờ xử lý';
        document.getElementById('detailEndDate').textContent = policy.end_date ? formatDate(policy.end_date) : 'Chờ xử lý';
        document.getElementById('detailCreatedAt').textContent = formatDateTime(policy.created_at);

        // Trạng thái
        const statusElement = document.getElementById('detailStatus');
        const statusInfo = statusMapping[policy.policy_status];
        statusElement.textContent = statusInfo.text;
        statusElement.className = `px-2 py-1 rounded-full text-sm ${statusInfo.class}`;

        // Thông tin khách hàng
        const customer = policy.customer;
        const user = customer.user;
        document.getElementById('detailCustomerName').textContent = `${user.first_name} ${user.last_name}`;
        document.getElementById('detailIdCard').textContent = customer.id_card_number;
        document.getElementById('detailDob').textContent = user.date_of_birth ? formatDate(user.date_of_birth) : 'Chưa cập nhật';
        document.getElementById('detailGender').textContent = genderMapping[customer.gender] || customer.gender;
        document.getElementById('detailPhone').textContent = user.phone_number || 'Chưa cập nhật';
        document.getElementById('detailEmail').textContent = user.email;
        document.getElementById('detailAddress').textContent = user.address || 'Chưa cập nhật';
        document.getElementById('detailJob').textContent = customer.job || 'Chưa cập nhật';
        document.getElementById('detailNationality').textContent = customer.nationality;

        // Thông tin sức khỏe
        const healthInfo = policy.health_info;
        if (healthInfo) {
            document.getElementById('detailHeight').textContent = `${healthInfo.height} cm`;
            document.getElementById('detailWeight').textContent = `${healthInfo.weight} kg`;
            document.getElementById('detailSmoker').textContent = smokingMapping[healthInfo.smoker] || healthInfo.smoker;
            document.getElementById('detailAlcohol').textContent = alcoholMapping[healthInfo.alcohol] || healthInfo.alcohol;
            document.getElementById('detailConditions').textContent =
                healthInfo.conditions && healthInfo.conditions.length > 0 ?
                healthInfo.conditions.join(', ') : 'Không có';
        }

        // File đính kèm
        renderFileSection('cccdFrontSection', customer.cccd_front, 'CCCD Mặt trước');
        renderFileSection('cccdBackSection', customer.cccd_back, 'CCCD Mặt sau');
        renderFileSection('selfieSection', customer.selfie, 'Ảnh Selfie');
        renderFileSection('healthCertificateSection', customer.health_certificate, 'Giấy khám sức khỏe');

        // Hiển thị/ẩn phần kiểm tra điều kiện và nút duyệt
        const approvalSection = document.getElementById('approvalConditionsSection');
        const approvalActions = document.getElementById('approvalActions');

        if (policy.policy_status === 'pending') {
            approvalSection.classList.remove('hidden');
            approvalActions.classList.remove('hidden');
            checkApprovalConditions(policy);
        } else {
            approvalSection.classList.add('hidden');
            approvalActions.classList.add('hidden');
        }
    }

    // Hàm hiển thị file
    function renderFileSection(sectionId, fileUrl, fileName) {
        const section = document.getElementById(sectionId);
        if (fileUrl) {
            const fileExtension = fileUrl.split('.').pop().toLowerCase();
            const isImage = ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(fileExtension);

            if (isImage) {
                section.innerHTML = `
                    <div class="flex items-center space-x-3">
                        <div class="w-16 h-16 bg-gray-200 rounded-lg overflow-hidden">
                            <img src="${fileUrl}" alt="${fileName}"
                                 class="w-full h-full object-cover cursor-pointer"
                                 onclick="openImageModal('${fileUrl}', '${fileName}')">
                        </div>
                        <div>
                            <p class="text-sm font-medium text-gray-800">${fileName}</p>
                            <a href="${fileUrl}" target="_blank"
                               class="text-blue-600 hover:text-blue-800 text-sm">Xem full size</a>
                        </div>
                    </div>
                `;
            } else {
                section.innerHTML = `
                    <div class="flex items-center space-x-3">
                        <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                            <i class="fas fa-file-pdf text-blue-600"></i>
                        </div>
                        <div>
                            <p class="text-sm font-medium text-gray-800">${fileName}</p>
                            <a href="${fileUrl}" target="_blank"
                               class="text-blue-600 hover:text-blue-800 text-sm">Tải xuống</a>
                        </div>
                    </div>
                `;
            }
        } else {
            section.innerHTML = '<p class="text-gray-500 text-sm">Không có file</p>';
        }
    }

    // Hàm kiểm tra điều kiện duyệt
    function checkApprovalConditions(policy) {
        const conditionsList = document.getElementById('conditionsList');
        conditionsList.innerHTML = '';

        const conditions = [];

        // Kiểm tra thông tin khách hàng
        if (!policy.customer.user.first_name || !policy.customer.user.last_name) {
            conditions.push('<li class="text-red-600"><i class="fas fa-times mr-2"></i>Thiếu họ tên khách hàng</li>');
        } else {
            conditions.push('<li class="text-green-600"><i class="fas fa-check mr-2"></i>Họ tên khách hàng: Đầy đủ</li>');
        }

        // Kiểm tra CCCD
        if (!policy.customer.id_card_number) {
            conditions.push('<li class="text-red-600"><i class="fas fa-times mr-2"></i>Thiếu số CCCD</li>');
        } else {
            conditions.push('<li class="text-green-600"><i class="fas fa-check mr-2"></i>Số CCCD: Đã cung cấp</li>');
        }

        // Kiểm tra file đính kèm
        const requiredFiles = [
            { name: 'CCCD mặt trước', hasFile: !!policy.customer.cccd_front },
            { name: 'CCCD mặt sau', hasFile: !!policy.customer.cccd_back },
            { name: 'Ảnh selfie', hasFile: !!policy.customer.selfie }
        ];

        requiredFiles.forEach(file => {
            if (file.hasFile) {
                conditions.push(`<li class="text-green-600"><i class="fas fa-check mr-2"></i>${file.name}: Đã upload</li>`);
            } else {
                conditions.push(`<li class="text-red-600"><i class="fas fa-times mr-2"></i>${file.name}: Chưa upload</li>`);
            }
        });

        // Kiểm tra thanh toán
        if (policy.payment_status === 'completed') {
            conditions.push('<li class="text-green-600"><i class="fas fa-check mr-2"></i>Thanh toán: Đã thanh toán</li>');
        } else {
            conditions.push('<li class="text-red-600"><i class="fas fa-times mr-2"></i>Thanh toán: Chưa thanh toán</li>');
        }

        conditionsList.innerHTML = conditions.join('');
    }

    // Hàm format tiền tệ
    function formatCurrency(amount) {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(amount);
    }

    // Hàm format ngày
    function formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('vi-VN');
    }

    // Hàm format ngày giờ
    function formatDateTime(dateTimeString) {
        if (!dateTimeString) return '-';
        const date = new Date(dateTimeString);
        return date.toLocaleString('vi-VN');
    }

    // Đóng modal
    function closeModal() {
        detailModal.classList.add('hidden');
    }

    closeDetailModal.addEventListener('click', closeModal);
    closeDetailModalBtn.addEventListener('click', closeModal);

    // Modal xem ảnh lớn
     function openImageModal(imageUrl, title) {
        const imageModal = document.createElement('div');
        imageModal.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50';
        imageModal.innerHTML = `
            <div class="bg-white rounded-lg max-w-4xl max-h-full overflow-auto">
                <div class="p-4 border-b flex justify-between items-center">
                    <h3 class="text-lg font-semibold">${title}</h3>
                    <button onclick="this.parentElement.parentElement.parentElement.remove()"
                            class="text-gray-500 hover:text-gray-700">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="p-4">
                    <img src="${imageUrl}" alt="${title}" class="max-w-full max-h-96 object-contain">
                </div>
            </div>
        `;
        document.body.appendChild(imageModal);
    };

