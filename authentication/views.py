import json
from django.conf import settings
from threading import Thread
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, LoginForm
from django.contrib.auth.models import User
from django.contrib.auth import login as login_auth, logout as logout_auth
from email_validator import validate_email as ValidateEmail, EmailNotValidError, EmailSyntaxError, EmailUndeliverableError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt # 这个库可以禁用csrf保护机制，方便我们在前端通过ajax进行异步请求
from django.contrib import messages
from django.core.mail import BadHeaderError, send_mail

def register(request):
    """注册视图"""
    if request.method == 'GET':
        return render(request, 'authentication/register.html')

    elif request.method == 'POST':
        # 校验 使用表单验证
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = User.objects.create(
                username = username,
                email = email
            )
            user.set_password(password)
            user.is_active = False # 默认注册是非活跃状态
            user.save()

            # 发送邮件
            content = f"""
            请点击下方链接，激活账号：
            http://127.0.0.1:8000/authentication/verify_account/{user.username}/
            """
            t = Thread(
                target=send_mail,
                args=[
                    "激活账号[超凡账本]",
                    content,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                ],
            )
            t.start() # 多线程发送邮件
            return HttpResponse("请查收邮件，激活账号")

        context =  {
            'form': form,
            'values': request.POST,
        }
        return render(request, "authentication/register.html", context)


def login(request):
    """登录视图"""
    if request.method == 'GET':
        return render(request, 'authentication/login.html')
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login_auth(request, form.user)
            messages.success(request, f"欢迎回来, {form.user.username}!")
            return redirect(to='expense')
        context = {
            'form': form,
            'values': request.POST,
        }
        return render(request, "authentication/login.html", context)


def logout(request):
    """退出登录视图"""
    logout_auth(request)
    messages.success(request, '退出成功')
    return redirect(to='authentication:login')


def verify_account(request, username):
    """激活账户"""
    user = get_object_or_404(User, username=username, is_active=False)
    user.is_active = True
    user.save()
    messages.success(request, '账号激活成功，请登录！')
    return redirect('authentication:login')


@csrf_exempt
def validate_username(request):
    """验证用户名"""
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username') # 获取用户名
        if not username.strip():
            return JsonResponse({
                'status': 'error',
                'msg': '用户名为空',
            }, status=400)

        if not username.isalnum():
            return JsonResponse({
                'status': 'error',
                'msg': '用户名不合法，不能使用特殊符号'
            }, status=400)

        if User.objects.filter(username__iexact=username.strip()).exists():
            return JsonResponse({
                'status': 'error',
                'msg': '用户名已存在',
            }, status=400)
        else:
            return JsonResponse({
                'status': 'success',
                'msg': 'ok'
            })


@csrf_exempt
def validate_email(request):
    """检验邮箱"""
    data = json.loads(request.body)
    email = data.get('email')
    if not email.strip():
        return JsonResponse({
            'status': 'error',
            'msg': '邮箱为空',
        }, status=400)

    try:
        ValidateEmail(email, check_deliverability=False)
    except EmailSyntaxError as e:
        return JsonResponse({
            'status': 'error',
            'msg': '邮箱格式不正确',
        }, status=400)
    except EmailUndeliverableError as e:
        return JsonResponse({
            'status': 'error',
            'msg': '该邮箱域名无法接收邮件'
        }, status=400)
    except EmailNotValidError as e:
        return JsonResponse({
            'status': 'error',
            'msg': '邮箱地址无效',
        }, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse(
            {
                "status": "error",
                "msg": "该邮箱已被注册",
            },
            status=400,
        )
    else:
        return JsonResponse({
            'status': 'success',
            'msg': 'ok'
        })


