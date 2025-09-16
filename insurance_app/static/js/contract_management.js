
        function switchTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.style.display = 'none';
            });

            // Remove active class from all tab buttons
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.className = btn.className.replace('tab-active', 'tab-inactive');
            });

            // Show selected tab content
            document.getElementById(tabName + 'Tab').style.display = 'block';

            // Add active class to clicked tab button
            event.target.className = event.target.className.replace('tab-inactive', 'tab-active');
        }

        function editProfile() {
            // Enable form fields
            const form = document.querySelector('#profileTab form');
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.removeAttribute('readonly');
                input.removeAttribute('disabled');
            });

            // Show edit buttons
            document.getElementById('editButtons').style.display = 'flex';

            // Change edit button text
            event.target.innerHTML = '<i class="fas fa-times mr-1"></i>Hủy chỉnh sửa';
            event.target.onclick = cancelEdit;
        }

        function cancelEdit() {
            // Disable form fields
            const form = document.querySelector('#profileTab form');
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.setAttribute('readonly', '');
                if (input.tagName === 'SELECT') {
                    input.setAttribute('disabled', '');
                }
            });

            // Hide edit buttons
            document.getElementById('editButtons').style.display = 'none';

            // Reset edit button
            const editBtn = document.querySelector('#profileTab .text-blue-600');
            editBtn.innerHTML = '<i class="fas fa-edit mr-1"></i>Chỉnh sửa';
            editBtn.onclick = editProfile;
        }

        function saveProfile() {
            // Simulate saving
            const saveBtn = event.target;
            const originalText = saveBtn.innerHTML;
            saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Đang lưu...';
            saveBtn.disabled = true;

            setTimeout(() => {
                alert('✅ Cập nhật thông tin thành công!');
                cancelEdit();
                saveBtn.innerHTML = originalText;
                saveBtn.disabled = false;
            }, 1500);
        }

        function changeAvatar() {
            alert('📷 Chức năng thay đổi ảnh đại diện sẽ được cập nhật sớm!');
        }

        function changePassword() {
            const currentPassword = document.querySelector('#securityTab input[type="password"]:nth-of-type(1)').value;
            const newPassword = document.querySelector('#securityTab input[type="password"]:nth-of-type(2)').value;
            const confirmPassword = document.querySelector('#securityTab input[type="password"]:nth-of-type(3)').value;

            if (!currentPassword || !newPassword || !confirmPassword) {
                alert('❌ Vui lòng điền đầy đủ thông tin!');
                return;
            }

            if (newPassword !== confirmPassword) {
                alert('❌ Mật khẩu xác nhận không khớp!');
                return;
            }

            if (newPassword.length < 8) {
                alert('❌ Mật khẩu phải có ít nhất 8 ký tự!');
                return;
            }

            // Simulate password change
            const btn = event.target;
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Đang cập nhật...';
            btn.disabled = true;

            setTimeout(() => {
                alert('✅ Đổi mật khẩu thành công!');
                // Clear form
                document.querySelectorAll('#securityTab input[type="password"]').forEach(input => {
                    input.value = '';
                });
                btn.innerHTML = originalText;
                btn.disabled = false;
            }, 2000);
        }

        function toggleSwitch(element) {
            element.classList.toggle('active');
        }

// Password strength indicator
document.querySelector('#securityTab input[type="password"]:nth-of-type(2)').addEventListener('input', function(e) {
    const password = e.target.value;
    const progressBar = document.querySelector('.progress-bar');

    let strength = 0;
    if (password.length >= 8) strength += 25;
    if (/[A-Z]/.test(password)) strength += 25;
    if (/[0-9]/.test(password)) strength += 25;
    if (/[^A-Za-z0-9]/.test(password)) strength += 25;

    progressBar.style.width = strength + '%';

    if (strength < 50) {
        progressBar.style.background = 'linear-gradient(90deg, #ef4444, #dc2626)';
    } else if (strength < 75) {
        progressBar.style.background = 'linear-gradient(90deg, #f59e0b, #d97706)';
    } else {
        progressBar.style.background = 'linear-gradient(90deg, #10b981, #059669)';
    }
});

// Handle button clicks
document.addEventListener('click', function(e) {
    const button = e.target.closest('button');
    if (!button) return;

    const buttonText = button.textContent.trim();

    if (buttonText.includes('Tải hợp đồng')) {
        alert('📄 Đang tải xuống file PDF hợp đồng...');
    } else if (buttonText.includes('In thẻ bảo hiểm')) {
        alert('🖨️ Yêu cầu in thẻ bảo hiểm đã được gửi. Thẻ sẽ được giao trong 3-5 ngày làm việc.');
    } else if (buttonText.includes('Giới thiệu bạn bè')) {
        alert('🎁 Mã giới thiệu của bạn: SECURE2024. Chia sẻ để nhận ưu đãi!');
    } else if (buttonText.includes('Xóa tài khoản')) {
        if (confirm('⚠️ Bạn có chắc chắn muốn xóa tài khoản? Hành động này không thể hoàn tác!')) {
            alert('📧 Chúng tôi đã gửi email xác nhận. Vui lòng kiểm tra hộp thư để hoàn tất.');
        }
    } else if (buttonText.includes('Câu hỏi thường gặp')) {
        alert('❓ Chuyển đến trang FAQ...');
    } else if (buttonText.includes('Chat với tư vấn viên')) {
        alert('💬 Mở cửa sổ chat với tư vấn viên...');
    } else if (buttonText.includes('Gọi hotline')) {
        alert('📞 Đang kết nối với tổng đài 1900 1234...');
    } else if (buttonText.includes('Đăng xuất tất cả')) {
        if (confirm('🔐 Bạn có chắc chắn muốn đăng xuất khỏi tất cả thiết bị khác?')) {
            alert('✅ Đã đăng xuất khỏi tất cả thiết bị khác thành công!');
        }
    } else if (buttonText.includes('Đăng xuất') && !buttonText.includes('tất cả')) {
        alert('📱 Đã đăng xuất khỏi thiết bị Safari trên iPhone!');
        button.closest('.flex').remove();
    } else if (buttonText.includes('Lưu cài đặt')) {
        const btn = button;
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Đang lưu...';
        btn.disabled = true;

        setTimeout(() => {
            alert('✅ Cài đặt thông báo đã được lưu!');
            btn.innerHTML = originalText;
            btn.disabled = false;
        }, 1500);
    }
});

// Notification bell
document.querySelector('.fa-bell').closest('button').addEventListener('click', function() {
    alert('🔔 Bạn có 3 thông báo mới:\n• Hợp đồng #SH2024001 sắp đến hạn gia hạn\n• Yêu cầu bồi thường #BC2024003 đã được phê duyệt\n• Khuyến mãi đặc biệt dành cho khách hàng VIP');
});
