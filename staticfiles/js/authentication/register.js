document.addEventListener('DOMContentLoaded', function () {
    const usernameInput = document.querySelector('#username');
    const emailInput = document.querySelector('#email');

    // 用户名验证
    if (usernameInput) {
        usernameInput.addEventListener('keyup', (e) => {
            const username = e.target.value;
            e.target.classList.remove('is-invalid');
            const feedback = e.target.closest('.input-group').querySelector('.invalid-feedback');
            if (feedback) feedback.innerText = '';

            fetch('/authentication/validate_username/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ "username": username }),
            })
                .then((res) => res.json())
                .then((data) => {
                    if (data.status == 'error') {
                        e.target.classList.add('is-invalid');
                        if (feedback) feedback.innerText = data.msg;
                    }
                });
        });
    }

    // 邮箱验证
    if (emailInput) {
        emailInput.addEventListener('keyup', (e) => {
            const email = e.target.value;
            e.target.classList.remove('is-invalid');
            const feedback = e.target.closest('.input-group').querySelector('.invalid-feedback');
            if (feedback) feedback.innerText = '';

            fetch('/authentication/validate_email/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ "email": email }),
            })
                .then((res) => res.json())
                .then((data) => {
                    if (data.status == 'error') {
                        e.target.classList.add('is-invalid');
                        if (feedback) feedback.innerText = data.msg;
                    }
                });
        });
    }

    // 密码显示切换
    function setupPasswordToggle(toggleId, inputId, iconId) {
        const toggle = document.querySelector(toggleId);
        const input = document.querySelector(inputId);
        const icon = document.querySelector(iconId);

        if (toggle && input && icon) {
            toggle.addEventListener('click', function () {
                const type = input.getAttribute('type');
                if (type === 'password') {
                    input.setAttribute('type', 'text');
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    input.setAttribute('type', 'password');
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            });
        }
    }

    setupPasswordToggle('#toggle-password', '#password', '#password-icon');
    setupPasswordToggle('#toggle-re-password', '#re_password', '#re-password-icon');
});
