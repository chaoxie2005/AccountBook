from django import forms  
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        error_messages={
            'required': '用户名为空'
        }
        )
    email = forms.EmailField(error_messages={"required": "邮箱为空"})
    password = forms.CharField(
        min_length=6,
        max_length=20,
        error_messages={
            "min_length": "密码不能少于6位",
            "max_length": "密码不能大于20位",
            "required": "密码不能为空",
        },
    )
    re_password = forms.CharField(
        min_length=6,
        max_length=20,
        error_messages={
            "min_length": "密码不能少于6位",
            "max_length": "密码不能大于20位",
            "required": "密码不能为空",
        },
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).first():
            self.add_error('username', '用户已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).first():
            self.add_error('email', '邮箱已存在')
        return email

    def clean_re_password(self):
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')
        if password and re_password and password != re_password:
            self.add_error('re_password', '两次密码输入不一致！')
        return re_password


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        error_messages={
            'required': '用户名为空',
        }
    )
    password = forms.CharField(
        min_length=6,
        max_length=20,
        error_messages={
            "min_length": "密码不能少于6位",
            "max_length": "密码不能大于20位",
            "required": "密码不能为空",
        },
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
           self.user = authenticate(username=username, password=password)
           if self.user is None:
               raise forms.ValidationError(
                   '密码或账号错误，请重试！', code='invalid_login'
               ) 
        return self.cleaned_data