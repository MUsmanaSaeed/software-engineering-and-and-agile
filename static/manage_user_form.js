document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('userForm');
    const messageDiv = document.getElementById('formMessage');
    [form.userName, form.password].forEach(function(input) {
        if (input) {
            input.addEventListener('input', function() {
                if (input.classList.contains('is-invalid')) {
                    if ((input.name === 'userName' && input.value.length >= 3) ||
                        (input.name === 'password' && (input.value.length === 0 || input.value.length >= 8))) {
                        input.classList.remove('is-invalid');
                    }
                }
            });
        }
    });
    function showMessage(html) {
        messageDiv.innerHTML = html;
        // Force reflow to restart animation if needed
        void messageDiv.offsetWidth;
        messageDiv.classList.add('show');
        // Remove any previous listeners
        removeInputListeners();
        // Add listeners to hide message only when all fields are valid/changed
        addInputListeners();
    }
    function hideMessage() {
        messageDiv.classList.remove('show');
        // Don't clear innerHTML until the transition is done
        const onTransitionEnd = (e) => {
            if (e.propertyName === 'opacity') {
                messageDiv.innerHTML = '';
                messageDiv.removeEventListener('transitionend', onTransitionEnd);
            }
        };
        messageDiv.addEventListener('transitionend', onTransitionEnd);
    }
    // Remove previous listeners
    function removeInputListeners() {
        if (form._clearMessageListeners) {
            form._clearMessageListeners.forEach(({el, fn, evt}) => el.removeEventListener(evt, fn));
        }
        form._clearMessageListeners = [];
    }
    // Add listeners to hide message only when all conditions are met
    function addInputListeners() {
        form._clearMessageListeners = [];
        const tryHide = () => {
            setTimeout(() => {
                // Only hide if the current message is related to the requirement and the requirement is now met
                const messageText = messageDiv.textContent.trim();
                if (
                    (messageText.includes('Username must be at least') && form.userName.value.length >= 3) ||
                    (messageText.includes('Password must be at least') && (form.password.value.length >= 8 || form.password.value.length === 0))
                ) {
                    hideMessage();
                    removeInputListeners();
                }
            }, 0);
        };
        form.userName.addEventListener('input', tryHide);
        form._clearMessageListeners.push({el: form.userName, fn: tryHide, evt: 'input'});
        if (form.password) {
            form.password.addEventListener('input', tryHide);
            form._clearMessageListeners.push({el: form.password, fn: tryHide, evt: 'input'});
        }
        if (form.isAdmin && !form.isAdmin.disabled) {
            form.isAdmin.addEventListener('change', tryHide);
            form._clearMessageListeners.push({el: form.isAdmin, fn: tryHide, evt: 'change'});
        }
    }
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        fetch(window.location.pathname, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            body: formData
        })
        .then(response => response.json().then(data => ({ status: response.status, body: data })))
        .then(({ status, body }) => {
            // Do not hide the message immediately
            if (body.success) {
                if (body.redirect) {
                    window.location.href = body.redirect;
                    return;
                }
                showMessage(`<div class='alert alert-success'>${body.message}</div>`);
                if (body.user) {
                    form.userName.value = body.user.userName;
                    if (form.isAdmin) form.isAdmin.checked = body.user.isAdmin;
                }
                form.password.value = '';
            } else {
                showMessage(`<div class='alert alert-danger'>${body.message || 'An error occurred.'}</div>`);
                // Highlight invalid fields
                if (body.error_fields) {
                    if (body.error_fields.includes('userName')) form.userName.classList.add('is-invalid');
                    if (body.error_fields.includes('password')) form.password.classList.add('is-invalid');
                }
            }
        })
        .catch(() => {
            showMessage(`<div class='alert alert-danger'>An error occurred. Please try again.</div>`);
        });
    });
});
