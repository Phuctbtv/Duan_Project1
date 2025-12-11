
// Biến toàn cục cho biểu đồ
let revenueChart, contractChart;
const el = document.getElementById("dashboard-data");

const isAdmin = el.dataset.isAdmin === "True";
const isAgent = el.dataset.isAgent === "True";

let revenueLabel = isAdmin
    ? "Doanh Thu (tỷ VNĐ)"
    : "Doanh Thu (triệu VNĐ)";

let revenueText = isAdmin
    ? "Tỷ VNĐ"
    : "Triệu VNĐ";
// Hàm khởi tạo biểu đồ với dữ liệu
function initializeCharts(data) {
    console.log('🎯 Khởi tạo biểu đồ với data:', data);

    // Xóa biểu đồ cũ nếu tồn tại
    if (revenueChart) revenueChart.destroy();
    if (contractChart) contractChart.destroy();

    // Biểu đồ doanh thu
    const revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        console.log('📊 Tạo revenue chart với data:', data.revenue_chart);

        // 1. Khai báo nhãn mặc định đủ 12 tháng
        const defaultLabels = ['Th1', 'Th2', 'Th3', 'Th4', 'Th5', 'Th6', 'Th7', 'Th8', 'Th9', 'Th10', 'Th11', 'Th12'];
        // 2. Khai báo mảng dữ liệu mặc định 12 tháng (tất cả là 0)
        const defaultData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];

        // LUÔN LUÔN DÙNG 12 THÁNG MẶC ĐỊNH CHO LABELS
        const labels = defaultLabels;

        let actualData = [];
        if (data.revenue_chart && Array.isArray(data.revenue_chart.data)) {
            actualData = data.revenue_chart.data;
        }

        // Tạo mảng 12 điểm dữ liệu.
        // Lấy dữ liệu thực tế, sau đó nối (concat) thêm các giá trị 0
        // để đạt đủ 12 phần tử, nếu cần.
        const requiredLength = 12;
        const chartData = actualData.concat(defaultData.slice(actualData.length));
        chartData.length = requiredLength; // Đảm bảo độ dài không vượt quá 12 nếu có lỗi dữ liệu



        revenueChart = new Chart(revenueCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: revenueLabel,
                    data: chartData,
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                // ... (Các tùy chọn khác giữ nguyên)
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: revenueText
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Tháng'
                        }
                    }
                }
            }
        });
        console.log('✅ Revenue chart created');
    } else {
        console.error('❌ Không tìm thấy revenueChart canvas');
    }


    // Biểu đồ phân loại hợp đồng
    const contractCtx = document.getElementById('contractChart');
    if (contractCtx) {
        console.log('📈 Tạo contract chart với data:', data.contract_chart);
        contractChart = new Chart(contractCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: data.contract_chart.labels || ['Không có dữ liệu'],
                datasets: [{
                    data: data.contract_chart.data || [1],
                    backgroundColor: [
                        '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#84cc16'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Phân Loại Hợp Đồng'
                    }
                }
            }
        });
        console.log('✅ Contract chart created');
    } else {
        console.error('❌ Không tìm thấy contractChart canvas');
    }
}

// Hàm làm mới biểu đồ với API
function refreshCharts(event) {
    console.log('🔄 Làm mới biểu đồ...');

    const refreshBtn = event.target.closest('button');
    const originalHtml = refreshBtn.innerHTML;
    refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Đang cập nhật...';
    refreshBtn.disabled = true;

    fetch('/admin/data/')
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log('📥 Data nhận được:', data);
            initializeCharts(data); // KHỞI TẠO LẠI hoàn toàn
            refreshBtn.innerHTML = originalHtml;
            refreshBtn.disabled = false;
            showNotification('Dữ liệu đã được cập nhật thành công!', 'success');
        })
        .catch(error => {
            console.error('❌ Lỗi khi cập nhật biểu đồ:', error);
            refreshBtn.innerHTML = originalHtml;
            refreshBtn.disabled = false;
            showNotification('Có lỗi khi cập nhật dữ liệu.', 'error');
        });
}



// Hàm hiển thị thông báo (giữ nguyên)
function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 transform transition-all duration-300 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;

    const icon = type === 'success' ? 'fa-check-circle' :
                 type === 'error' ? 'fa-exclamation-circle' :
                 'fa-info-circle';

    toast.innerHTML = `
        <div class="flex items-center">
            <i class="fas ${icon} mr-2"></i>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(toast);

    // Tự động xóa sau 4 giây
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 4000);
}

// Khởi tạo biểu đồ khi trang load
document.addEventListener('DOMContentLoaded', function() {
    // Gọi API ngay khi trang load để lấy dữ liệu thực
    fetch('/admin/data/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Dữ liệu khởi tạo:', data);
            initializeCharts(data);
        })
        .catch(error => {
            console.error('Lỗi khi tải dữ liệu ban đầu:', error);
            // Khởi tạo với dữ liệu mẫu nếu API lỗi
            initializeCharts({});
            showNotification('Đang sử dụng dữ liệu mẫu. Vui lòng cập nhật để lấy dữ liệu thực.', 'info');
        });
});
