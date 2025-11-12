
    let currentApprovalStep = 1;
    let currentPage = 1;
    const itemsPerPage = 5;
    let claims = [];
    let filteredClaims = [];

    document.addEventListener("DOMContentLoaded", function() {
        fetch('/custom_claims/api/claims/?page_size=1000')
          .then(res => res.json())
          .then(data => {
              claims = data.claims;
              filteredClaims = data.claims;
              renderClaims();
              renderPagination();
          });
    });

    // Render claims list
    function renderClaims() {
        const container = document.getElementById('claimsList');
        container.innerHTML = '';

        // Lấy dữ liệu theo trang
        const start = (currentPage - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const pageData = filteredClaims.slice(start, end);

        pageData.forEach(claim => {
            const claimCard = createClaimCard(claim);
            container.appendChild(claimCard);
        });
    }

    // --- Render nút phân trang ---
    function renderPagination() {
        const paginationContainer = document.getElementById("pagination");
        paginationContainer.innerHTML = "";

        const totalPages = Math.ceil(filteredClaims.length / itemsPerPage);
        if (totalPages <= 1) return; // Không cần hiển thị nếu chỉ có 1 trang

        const paginationHTML = `
            <div class="flex justify-center items-center gap-2 mt-6">
                <button class="px-3 py-1 border rounded ${currentPage === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100'}"
                    onclick="changePage(1)">Đầu</button>
                <button class="px-3 py-1 border rounded ${currentPage === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100'}"
                    onclick="changePage(${currentPage - 1})">Trước</button>

                <span class="px-3 py-1 bg-blue-500 text-white rounded">Trang ${currentPage} / ${totalPages}</span>

                <button class="px-3 py-1 border rounded ${currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100'}"
                    onclick="changePage(${currentPage + 1})">Sau</button>
                <button class="px-3 py-1 border rounded ${currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100'}"
                    onclick="changePage(${totalPages})">Cuối</button>
            </div>
        `;
        paginationContainer.innerHTML = paginationHTML;
    }

    // --- Chuyển trang ---
    function changePage(page) {
        const totalPages = Math.ceil(filteredClaims.length / itemsPerPage);
        if (page < 1 || page > totalPages) return;
        currentPage = page;
        renderClaims();
        renderPagination();
    }
    // Create claim card
    function createClaimCard(claim) {
        const card = document.createElement('div');
        card.className = 'claim-card bg-white rounded-xl shadow-sm p-6 cursor-pointer';
        card.onclick = () => selectClaim(claim);

        const statusColors = {
            pending: 'bg-orange-100 text-orange-800',
            in_progress: 'bg-blue-100 text-blue-800',
            request_more: 'bg-blue-100 text-blue-800',
            approved: 'bg-green-100 text-green-800',
            rejected: 'bg-red-100 text-red-800'
        };

        const statusTexts = {
            pending: 'Chờ xét duyệt',
            in_progress: 'Đang xem xét',
            approved: 'Đã phê duyệt',
            request_more: 'Yêu cầu bổ sung tài liệu',
            rejected: 'Từ chối'
        };

        const priorityColors = {
            high: 'text-red-600',
            medium: 'text-yellow-600',
            low: 'text-green-600'
        };

        card.innerHTML = `
            <div class="flex items-center justify-between mb-4">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <i class="fas fa-file-medical text-blue-600"></i>
                    </div>
                    <div>
                        <h3 class="font-bold text-gray-800">${claim.claim_number}</h3>
                        <p class="text-sm text-gray-600">${claim.customer_name}</p>
                    </div>
                </div>
                <div class="flex items-center space-x-2">
                    <span class="status-badge ${statusColors[claim.claim_status]}">${statusTexts[claim.claim_status]}</span>
                    <i class="fas fa-exclamation-circle ${priorityColors[claim.priority] || 'text-red-400'}"></i>

                </div>
            </div>

            <div class="grid md:grid-cols-3 gap-4 text-sm mb-4">
                <div>
                    <span class="text-gray-600">Ngày sự cố:</span>
                    <span class="font-semibold ml-1">${formatDate(claim.incident_date)}</span>
                </div>
                <div>
                    <span class="text-gray-600">Bệnh viện:</span>
                    <span class="font-semibold ml-1">
                        ${claim.medical_info?.[0]?.hospital_name || 'Chưa có'}
                    </span>

                </div>
                <div>
                    <span class="text-gray-600">Số tiền yêu cầu:</span>
                    <span class="font-semibold ml-1 text-red-600">${formatCurrency(claim.requested_amount)}</span>
                </div>
            </div>

            <div class="flex items-center justify-between">
                <div class="text-sm text-gray-600">
                    <i class="fas fa-calendar mr-1"></i>
                    Nộp: ${formatDate(claim.created_at)}
                </div>
                <div class="flex items-center space-x-2">
                    <span class="text-sm text-gray-600">${claim.documents_count} tài liệu</span>
                    <i class="fas fa-chevron-right text-gray-400"></i>
                </div>
            </div>
        `;

        return card;
    }

    // Select claim
    function selectClaim(claim) {
        selectedClaim = claim;
        renderClaimDetails(claim);

        // Highlight selected card
        document.querySelectorAll('.claim-card').forEach(card => {
            card.classList.remove('ring-2', 'ring-blue-500');
        });
        event.currentTarget.classList.add('ring-2', 'ring-blue-500');
    }

    // Render claim details
    function renderClaimDetails(claim) {
        const panel = document.getElementById('claimDetailsPanel');

        const statusColors = {
            pending: 'bg-orange-100 text-orange-800',
            in_progress: 'bg-blue-100 text-blue-800',
            request_more: 'bg-blue-100 text-blue-800',
            approved: 'bg-green-100 text-green-800',
            settled: 'bg-green-100 text-green-800',
            rejected: 'bg-red-100 text-red-800'
        };

        const statusTexts = {
            pending: 'Chờ xét duyệt',
            in_progress: 'Đang xem xét',
            approved: 'Đã phê duyệt',
            request_more:'Yêu cầu bổ sung tài liệu',
            rejected: 'Từ chối',
            settled:'Đã giải quyết'
        };

        panel.innerHTML = `
            <div class="fade-in">
                <div class="flex items-center justify-between mb-6">
                    <h3 class="text-lg font-bold text-gray-800">Chi tiết yêu cầu</h3>
                   <span class="status-badge ${statusColors[claim.claim_status]}">${statusTexts[claim.claim_status]}</span>
                </div>

                <div class="space-y-4 mb-6">
                    <div>
                        <label class="text-sm text-gray-600">Mã yêu cầu</label>
                        <p class="font-semibold">${claim.claim_number}</p>
                    </div>
                    <div>
                        <label class="text-sm text-gray-600">Khách hàng</label>
                        <p class="font-semibold">${claim.customer_name}</p>
                    </div>
                    <div>
                        <label class="text-sm text-gray-600">Hợp đồng</label>
                        <p class="font-semibold">${claim.policy}</p>
                    </div>
                    <div>
                        <label class="text-sm text-gray-600">Sản phẩm</label>
                        <p class="font-semibold">${claim.product_name}</p>
                    </div>
                    <div>
                        <label class="text-sm text-gray-600">Chẩn đoán</label>
                        <p class="font-semibold">${claim.medical_info[0].diagnosis}</p>
                    </div>
                    <div>
                        <label class="text-sm text-gray-600">Số tiền yêu cầu</label>
                        <p class="font-semibold text-red-600">${formatCurrency(claim.requested_amount)}</p>
                    </div>
                </div>

                <div class="space-y-3 mb-6">
                    <h4 class="font-semibold text-gray-800">Tài liệu</h4>
                    ${claim.documents.map(doc => `
                        <div class="flex items-center justify-between p-2 bg-gray-50 rounded">
                            <span class="text-sm">${doc.document_type}</span>
                            <a href="${doc.file_url}" target="_blank">
                                <i class="fas fa-eye text-blue-600 cursor-pointer"></i>
                            </a>
                        </div>
                    `).join('')}

                </div>

                ${claim.claim_status === 'pending' || claim.claim_status === 'in_progress' || claim.claim_status === 'request_more' ? `
                    <button onclick="openApprovalModal()" class="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700">
                        <i class="fas fa-clipboard-check mr-2"></i>Xét duyệt
                    </button>
                ` : ''}

                <div class="mt-4 space-y-2">
                    <button onclick="viewHistory()" class="w-full bg-gray-200 text-gray-700 py-2 rounded-lg text-sm hover:bg-gray-300">
                        <i class="fas fa-history mr-2"></i>Lịch sử xử lý
                    </button>
                    <button onclick="exportReport()" class="w-full bg-gray-200 text-gray-700 py-2 rounded-lg text-sm hover:bg-gray-300">
                        <i class="fas fa-download mr-2"></i>Xuất báo cáo
                    </button>
                </div>
            </div>
        `;
    }

    // Filter claims
    function filterClaims() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        const statusFilter = document.getElementById('statusFilter').value;
        const typeFilter = document.getElementById('typeFilter').value;

         filteredClaims = claims.filter(claim => {
            const matchesSearch = claim.claim_number.toLowerCase().includes(searchTerm) ||
                                claim.customer_name.toLowerCase().includes(searchTerm);
            const matchesStatus = !statusFilter || claim.claim_status === statusFilter;
            const matchesType = !typeFilter || claim.medical_info.treatmentType === typeFilter;

            return matchesSearch && matchesStatus && matchesType;
        });
        currentPage = 1;

        renderClaims();
        renderPagination();
    }


    // Open approval modal
    function openApprovalModal() {
        if (!selectedClaim) return;

        document.getElementById('approvalModal').classList.remove('hidden');
        document.body.style.overflow = 'hidden';

        // Reset modal state
        currentApprovalStep = 1;
        resetApprovalSteps();
        populateApprovalData();
    }

    // Close approval modal
    function closeApprovalModal() {
        document.getElementById('approvalModal').classList.add('hidden');
        document.body.style.overflow = 'auto';
    }

    // Reset approval steps
    function resetApprovalSteps() {
        // Hide all step contents
        for (let i = 1; i <= 3; i++) {
            document.getElementById(`approvalStepContent${i}`).classList.add('hidden');
        }

        // Reset step indicators
        for (let i = 1; i <= 3; i++) {
            const step = document.getElementById(`approvalStep${i}`);
            step.className = 'approval-step w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 font-bold';
            step.textContent = i;
        }

        // Reset lines
        for (let i = 1; i <= 2; i++) {
            document.getElementById(`approvalLine${i}`).className = 'w-16 h-1 bg-gray-200';
        }

        // Show first step
        document.getElementById('approvalStep1').classList.add('active');
        document.getElementById('approvalStepContent1').classList.remove('hidden');
    }

    // Populate approval data
    function populateApprovalData() {
        if (!selectedClaim) return;

        // Populate claim info
        const claimInfo = document.getElementById('claimInfo');
        claimInfo.innerHTML = `
            <div>
                <span class="text-blue-600">Mã yêu cầu:</span>
                <span class="font-bold ml-2">${selectedClaim.claim_number}</span>
            </div>
            <div>
                <span class="text-blue-600">Khách hàng:</span>
                <span class="font-bold ml-2">${selectedClaim.customer_name}</span>
            </div>
            <div>
                <span class="text-blue-600">Trạng thái:</span>
                <span class="font-bold ml-2">${selectedClaim.claim_status}</span>
            </div>

            <div>
                <span class="text-blue-600">Ngày xảy ra sự cố:</span>
                <span class="font-bold ml-2">${formatDate(selectedClaim.incident_date)}</span>
            </div>
            <div>
                <span class="text-blue-600">Mô tả chi tiết:</span>
                <span class="font-bold ml-2">${(selectedClaim.description)}</span>
            </div>

            <div>
                <span class="text-blue-600">Số tiền khách yêu cầu:</span>
                <span class="font-bold ml-2 text-red-600">${formatCurrency(selectedClaim.requested_amount)}</span>
            </div>
        `;

        // Populate claim medicalinfo
        const claimMedicalInfo = document.getElementById('ClaimMedicalInfo');
        claimMedicalInfo.innerHTML = `
            <div>
                <span class="text-blue-600">Loại điều trị:</span>
                <span class="font-bold ml-2">${selectedClaim.medical_info[0].treatment_type}</span>
            </div>
            <div>
                <span class="text-blue-600">Bệnh viện:</span>
                <span class="font-bold ml-2">${selectedClaim.medical_info[0].hospital_name}</span>
            </div>
            <div>
                <span class="text-blue-600">Bác sĩ điều trị:</span>
                <span class="font-bold ml-2">${selectedClaim.medical_info[0].doctor_name}</span>
            </div>

            <div>
                <span class="text-blue-600">Địa chỉ bệnh viện:</span>
                <span class="font-bold ml-2">${(selectedClaim.medical_info[0].hospital_address)}</span>
            </div>
            <div>
                <span class="text-blue-600">Chẩn đoán:</span>
                <span class="font-bold ml-2">${selectedClaim.medical_info[0].diagnosis}</span>
            </div>
            <div>
                <span class="text-blue-600">Ngày nhập viện:</span>
                <span class="font-bold ml-2">${formatDate(selectedClaim.medical_info[0].admission_date)}</span>
            </div>
            <div>
                <span class="text-blue-600">Ngày xuất viện:</span>
                <span class="font-bold ml-2">${formatDate(selectedClaim.medical_info[0].discharge_date)}</span>
            </div>
            <div>
                <span class="text-blue-600">Tổng chi phí điều trị:</span>
                <span class="font-bold ml-2 text-red-600">${formatCurrency(selectedClaim.medical_info[0].total_treatment_cost)}</span>
            </div>
        `;
        // Populate documents
        const documentsList = document.getElementById('documentsList');
        documentsList.innerHTML = selectedClaim.documents.map(doc => `
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div class="flex items-center">
                    <i class="fas fa-file-alt text-blue-600 mr-3"></i>
                    <span class="font-semibold">${doc.document_type}</span>
                </div>
                <a href="${doc.file_url}" target="_blank">
                    <i class="fas fa-eye text-blue-600 cursor-pointer"></i>
                </a>
            </div>
        `).join('');

        // Set requested amount
        document.getElementById('requestedAmount').value = formatCurrency(selectedClaim.requested_amount);
        document.getElementById('approvedAmount').value = selectedClaim.requested_amount;
    }
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Nếu cookie bắt đầu bằng tên bạn cần
                if (cookie.substring(0, name.length + 1) === name + "=") {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Next approval step
    async function nextApprovalStep() {
        if (currentApprovalStep >= 3) return;

        // Hide current step
        document.getElementById(`approvalStepContent${currentApprovalStep}`).classList.add('hidden');

        // Update step indicator
        const currentStepEl = document.getElementById(`approvalStep${currentApprovalStep}`);
        currentStepEl.classList.remove('active');
        currentStepEl.classList.add('completed');
        currentStepEl.innerHTML = '<i class="fas fa-check"></i>';

        // Update line
        if (currentApprovalStep < 3) {
            document.getElementById(`approvalLine${currentApprovalStep}`).classList.remove('bg-gray-200');
            document.getElementById(`approvalLine${currentApprovalStep}`).classList.add('bg-green-500');
        }

        // Move to next step
        currentApprovalStep++;

        // Show next step
        document.getElementById(`approvalStepContent${currentApprovalStep}`).classList.remove('hidden');
        document.getElementById(`approvalStep${currentApprovalStep}`).classList.add('active');

        //  Gọi API đánh giá rủi ro khi sang bước 2
        if (currentApprovalStep === 2) {
            try {
                const response = await fetch(`/custom_claims/api/claims/${selectedClaim.id}/risk-assessment/`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                });

                if (!response.ok) throw new Error('Đánh giá rủi ro thất bại');

                const data = await response.json();
                console.log('Kết quả đánh giá rủi ro:', data);

                const riskBox = document.getElementById('riskAssessmentBox');
                if (riskBox && data) {
                    // Màu + biểu tượng theo mức độ rủi ro
                    const riskStyles = {
                        low: {
                            color: 'text-green-700',
                            bg: 'bg-green-50',
                            border: 'border-green-400',
                            icon: '🟢',
                        },
                        medium: {
                            color: 'text-yellow-700',
                            bg: 'bg-yellow-50',
                            border: 'border-yellow-400',
                            icon: '🟡',
                        },
                        high: {
                            color: 'text-orange-700',
                            bg: 'bg-orange-50',
                            border: 'border-orange-400',
                            icon: '🟠',
                        },
                        very_high: {
                            color: 'text-red-700',
                            bg: 'bg-red-50',
                            border: 'border-red-500',
                            icon: '🔴',
                        },
                    };

                    const level = data.risk_level || 'low';
                    const style = riskStyles[level] || riskStyles.low;

                    // Tạo danh sách chi tiết
                    const detailsHtml = Object.entries(data.details || {})
                        .map(([_, value]) => `<li class="ml-4 list-disc">${value}</li>`)
                        .join("");

                    // Render HTML
                    riskBox.innerHTML = `
                        <div class="p-4 rounded-xl border ${style.border} ${style.bg} ${style.color} shadow-sm">
                            <p class="font-semibold text-lg flex items-center gap-2">
                                ${style.icon}
                                Mức độ rủi ro: <span class="uppercase">${data.risk_level_display}</span>
                            </p>
                            <p class="mt-1">Điểm rủi ro: <strong>${data.score}</strong></p>

                            ${
                                detailsHtml
                                    ? `<div class="mt-3">
                                        <p class="font-medium">Chi tiết đánh giá:</p>
                                        <ul class="mt-1 text-sm">${detailsHtml}</ul>
                                      </div>`
                                    : ''
                            }
                        </div>
                    `;
                }



            } catch (error) {
                console.error(error);
                alert('Lỗi khi đánh giá rủi ro. Vui lòng thử lại!');
            }
        }

        // Update final amounts in step 3
        if (currentApprovalStep === 3) {
            document.getElementById('finalRequestedAmount').textContent = formatCurrency(selectedClaim.requested_amount);
            const approvedAmount = document.getElementById('approvedAmount').value || selectedClaim.requested_amount;
            document.getElementById('finalApprovedAmount').textContent = formatCurrency(approvedAmount);
        }
    }


    // Previous approval step
    function prevApprovalStep() {
        if (currentApprovalStep <= 1) return;

        // Hide current step
        document.getElementById(`approvalStepContent${currentApprovalStep}`).classList.add('hidden');

        // Update step indicator
        document.getElementById(`approvalStep${currentApprovalStep}`).classList.remove('active');
        document.getElementById(`approvalStep${currentApprovalStep}`).classList.add('bg-gray-200', 'text-gray-600');
        document.getElementById(`approvalStep${currentApprovalStep}`).textContent = currentApprovalStep;

        // Move to previous step
        currentApprovalStep--;

        // Show previous step
        document.getElementById(`approvalStepContent${currentApprovalStep}`).classList.remove('hidden');

        // Update step indicator
        const prevStepEl = document.getElementById(`approvalStep${currentApprovalStep}`);
        prevStepEl.classList.remove('completed');
        prevStepEl.classList.add('active');
        prevStepEl.textContent = currentApprovalStep;

        // Update line
        if (currentApprovalStep < 3) {
            document.getElementById(`approvalLine${currentApprovalStep}`).classList.add('bg-gray-200');
            document.getElementById(`approvalLine${currentApprovalStep}`).classList.remove('bg-green-500');
        }
    }

    // Submit decision
    function submitDecision() {
        const decision = document.querySelector('input[name="decision"]:checked');
        const reason = document.getElementById('decisionReason').value;

        if (!decision || !reason.trim()) {
            alert('Vui lòng chọn quyết định và nhập lý do');
            return;
        }

        const formData = new FormData();
        const approvedAmount = document.getElementById('approvedAmount').value
        formData.append("decision", decision.value);
        formData.append("reason", reason);
        formData.append("approvedAmount", approvedAmount);
        fetch(`/custom_claims/${selectedClaim.id}/decision/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) throw new Error("Lỗi mạng hoặc quyền truy cập");
            return response.text();
        })
        .then(() => {

            const messages = {
                approve: 'Yêu cầu bồi thường đã được phê duyệt',
                reject: 'Yêu cầu bồi thường đã bị từ chối',
                request_more: 'Đã yêu cầu khách hàng bổ sung tài liệu'
            };

            document.getElementById('successMessage').textContent = messages[decision.value];
            closeApprovalModal();
            document.getElementById('successModal').classList.remove('hidden');
            renderClaims();
            renderClaimDetails(selectedClaim);
        })
        .catch(error => alert("Lỗi xử lý: " + error));
    }


    // Close success modal
    function closeSuccessModal() {
        document.getElementById('successModal').classList.add('hidden');
    }
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

    // Other functions
    function viewHistory() {
        alert('Hiển thị lịch sử xử lý yêu cầu...');
    }

    function exportReport() {
        alert('Xuất báo cáo yêu cầu bồi thường...');
    }

    // Helper functions
    function formatCurrency(amount) {
        return new Intl.NumberFormat('vi-VN', {
            style: 'decimal',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount) + ' VNĐ';
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('vi-VN');
    }

    // Close modals on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeApprovalModal();
            closeSuccessModal();
        }
    });

    document.getElementById('searchInput').addEventListener('input', filterClaims);
    document.getElementById('statusFilter').addEventListener('change', filterClaims);
    document.getElementById('typeFilter').addEventListener('change', filterClaims);
