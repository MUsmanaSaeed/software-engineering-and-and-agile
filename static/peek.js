// JavaScript for toggling password visibility on the login page

document.addEventListener('DOMContentLoaded', function() {
    // Support multiple password fields/buttons on the same page
    document.querySelectorAll('#togglePassword').forEach(function(toggle) {
        var password = toggle.closest('.position-relative').querySelector('#passwordInput');
        if (toggle && password) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
                password.setAttribute('type', type);
                const icon = toggle.querySelector('i');
                if (icon) {
                    icon.classList.toggle('bi-eye');
                    icon.classList.toggle('bi-eye-slash');
                }
                // Reset background after click
                toggle.style.background = '';
            });
            // Ensure background resets on mouseleave
            toggle.addEventListener('mouseleave', function() {
                toggle.style.background = '';
            });
        }
    });
});
