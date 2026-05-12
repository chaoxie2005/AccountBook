const passwordInput = document.querySelector('#password')
const re_passwordInput = document.querySelector('#re_password')
const eyeIcon = document.querySelector('#hide-password_1')
const re_eyeIcon = document.querySelector('#hide-password_2')


eyeIcon.addEventListener('click', (e) => {
    let type = passwordInput.getAttribute('type');
    if (type == 'password') {
        passwordInput.setAttribute('type', 'text');
        eyeIcon.setAttribute('src', '/static/img/authentication/eye_off.svg');
    } else {
        passwordInput.setAttribute('type', 'password');
        eyeIcon.setAttribute('src', '/static/img/authentication/eye.svg');
    }
})


re_eyeIcon.addEventListener('click', (e) => {
    let type = re_passwordInput.getAttribute('type');
    if (type == 'password') {
        re_passwordInput.setAttribute('type', 'text');
        re_eyeIcon.setAttribute('src', '/static/img/authentication/eye_off.svg');
    } else {
        re_passwordInput.setAttribute('type', 'password');
        re_eyeIcon.setAttribute('src', '/static/img/authentication/eye.svg');
    }
})