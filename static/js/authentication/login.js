document.addEventListener('DOMContentLoaded', function () {
    const togglePwd = document.querySelector('#toggle-password');
    const pwdInput = document.querySelector('#password');
    const pwdIcon = document.querySelector('#password-icon');
    const verifyImg = document.querySelector('#verify-code');

    // 切换密码可见性
    if (togglePwd && pwdInput && pwdIcon) {
        togglePwd.addEventListener('click', function () {
            const type = pwdInput.getAttribute('type');
            if (type === 'password') {
                pwdInput.setAttribute('type', 'text');
                pwdIcon.classList.remove('fa-eye');
                pwdIcon.classList.add('fa-eye-slash');
            } else {
                pwdInput.setAttribute('type', 'password');
                pwdIcon.classList.remove('fa-eye-slash');
                pwdIcon.classList.add('fa-eye');
            }
        });
    }

    // 刷新验证码
    if (verifyImg) {
        verifyImg.addEventListener('click', function () {
            // 获取当前的 src 路径（去掉旧的查询参数）
            const currentSrc = verifyImg.getAttribute('src').split('?')[0];
            verifyImg.setAttribute('src', currentSrc + '?' + Math.random());
        });
    }
});
