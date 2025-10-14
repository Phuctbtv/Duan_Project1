
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
        // Show notification

        document.addEventListener('DOMContentLoaded', function () {
            const toasts = document.querySelectorAll('#toast-container .toast');
            toasts.forEach(function (toast) {
                setTimeout(() => {
                    toast.style.opacity = '0';
                    toast.style.transform = 'translateY(-10px)';
                    setTimeout(() => toast.remove(), 500);
                }, 2000);
            });
        });