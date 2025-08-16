
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Add scroll effect to header
        window.addEventListener('scroll', function() {
            const header = document.querySelector('header');
            if (window.scrollY > 100) {
                header.classList.add('shadow-xl');
            } else {
                header.classList.remove('shadow-xl');
            }
        });

        // Interactive buttons
        document.querySelectorAll('button').forEach(button => {
            button.addEventListener('click', function() {
                // Add click animation
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = 'scale(1)';
                }, 150);

                // Show demo alerts for main actions
                const buttonText = this.textContent.trim();
                if (buttonText.includes('Tính phí')) {
                    alert('🧮 Tính năng tính phí bảo hiểm sẽ chuyển đến trang chi tiết sản phẩm!');
                } else if (buttonText.includes('Xem demo')) {
                    alert('🎥 Demo video sẽ hiển thị cách sử dụng hệ thống AI!');
                } else if (buttonText.includes('Tìm hiểu thêm')) {
                    alert('📋 Chuyển đến trang chi tiết sản phẩm với thông tin đầy đủ!');
                } else if (buttonText.includes('Đăng ký')) {
                    alert('📝 Chuyển đến trang đăng ký tài khoản mới!');
                } else if (buttonText.includes('Mua thêm')) {
                    alert('🛒 Chuyển đến trang danh sách sản phẩm bảo hiểm!');
                }
            });
        });

        // Add hover effects to cards
        document.querySelectorAll('.card-hover').forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px)';
            });

            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });