const eyeIcon = document.querySelector('#hide-password')
const pwdInput = document.querySelector('#password')

eyeIcon.addEventListener('click', (e) => {
    let type = pwdInput.getAttribute('type')
    if (type == 'password') {
        pwdInput.setAttribute('type', 'text')
        eyeIcon.setAttribute('src', '/static/img/authentication/eye_off.svg')
    } else {
        pwdInput.setAttribute('type', 'password')
        eyeIcon.setAttribute('src', '/static/img/authentication/eye.svg')
    }
})
