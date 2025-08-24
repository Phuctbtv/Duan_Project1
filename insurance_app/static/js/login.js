
        let currentForm = 'login';

        function togglePassword(inputId) {
            const input = document.getElementById(inputId);
            const icon = input.nextElementSibling.querySelector('i');

            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        }

        // Password strength checker
        document.getElementById('registerPassword')?.addEventListener('input', function(e) {
            const password = e.target.value;
            const length = document.getElementById('length');
            const uppercase = document.getElementById('uppercase');
            const number = document.getElementById('number');

            // Check length
            if (password.length >= 8) {
                length.classList.remove('text-gray-400');
                length.classList.add('text-green-500');
                length.querySelector('i').classList.remove('fa-times');
                length.querySelector('i').classList.add('fa-check');
            } else {
                length.classList.remove('text-green-500');
                length.classList.add('text-gray-400');
                length.querySelector('i').classList.remove('fa-check');
                length.querySelector('i').classList.add('fa-times');
            }

            // Check uppercase
            if (/[A-Z]/.test(password)) {
                uppercase.classList.remove('text-gray-400');
                uppercase.classList.add('text-green-500');
                uppercase.querySelector('i').classList.remove('fa-times');
                uppercase.querySelector('i').classList.add('fa-check');
            } else {
                uppercase.classList.remove('text-green-500');
                uppercase.classList.add('text-gray-400');
                uppercase.querySelector('i').classList.remove('fa-check');
                uppercase.querySelector('i').classList.add('fa-times');
            }

            // Check number
            if (/\d/.test(password)) {
                number.classList.remove('text-gray-400');
                number.classList.add('text-green-500');
                number.querySelector('i').classList.remove('fa-times');
                number.querySelector('i').classList.add('fa-check');
            } else {
                number.classList.remove('text-green-500');
                number.classList.add('text-gray-400');
                number.querySelector('i').classList.remove('fa-check');
                number.querySelector('i').classList.add('fa-times');
            }
        });

        // Form submissions
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function(e) {
                const button = this.querySelector('button[type="submit"]');
                if (!button) return;

                if (typeof currentForm !== "undefined" && currentForm === 'login') {
                    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Đang đăng nhập...';
                } else {
                    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Đang tạo tài khoản...';
                }
                button.disabled = true;
            });
        });



        // Social login buttons
        document.querySelectorAll('button').forEach(button => {
            if (button.textContent.includes('Google') || button.textContent.includes('Facebook')) {
                button.addEventListener('click', function() {
                    const platform = this.textContent.trim();
                    alert(`🔗 Chuyển đến đăng nhập ${platform}...`);
                });
            }
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

        // Input animations
        document.querySelectorAll('input').forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('transform', 'scale-105');
            });

            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('transform', 'scale-105');
            });
        });

