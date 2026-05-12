import json
from django.conf import settings
from threading import Thread
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from .forms import RegisterForm, LoginForm
from django.contrib.auth.models import User
from django.contrib.auth import login as login_auth, logout as logout_auth
from email_validator import (
    validate_email as ValidateEmail,
    EmailNotValidError,
    EmailSyntaxError,
    EmailUndeliverableError,
)
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import (
    csrf_exempt,
)  # 这个库可以禁用csrf保护机制，方便我们在前端通过ajax进行异步请求
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator  # django内置的生成token
from .models import UserInfo
from django.http import FileResponse

def register(request):
    """注册视图"""
    if request.method == "GET":
        return render(request, "authentication/register.html")

    elif request.method == "POST":
        # 校验 使用表单验证
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = User.objects.create(username=username, email=email)
            user.set_password(password)
            user.is_active = False  # 默认注册是非活跃状态
            user.save()

            # 发送邮件
            current_site = get_current_site(request)
            verify_url = request.build_absolute_uri(
                resolve_url("authentication:verify_account", user.username)
            )
            content = f"""
            您好 {user.username}，
            
            感谢注册超凡账本！请点击下方链接激活您的账号：
            {verify_url}
            
            如果您没有注册此账号，请忽略此邮件。
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
            t.start()  # 多线程发送邮件
            return HttpResponse("请查收邮件，激活账号")

        context = {
            "form": form,
            "values": request.POST,
        }
        return render(request, "authentication/register.html", context)


def login(request):
    """登录视图"""
    if request.method == "GET":
        form = LoginForm(request=request)
        return render(request, "authentication/login.html", {"form": form})
    elif request.method == "POST":
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            login_auth(request, form.user)
            messages.success(request, f"欢迎回来, {form.user.username}!")
            return redirect(to="expense")
        context = {
            "form": form,
            "values": request.POST,
        }
        return render(request, "authentication/login.html", context)


def logout(request):
    """退出登录视图"""
    logout_auth(request)
    messages.success(request, "退出成功")
    return redirect(to="authentication:login")


def verify_account(request, username):
    """激活账户"""
    user = get_object_or_404(User, username=username, is_active=False)
    user.is_active = True
    user.save()
    messages.success(request, "账号激活成功，请登录！")
    return redirect("authentication:login")


@csrf_exempt
def validate_username(request):
    """验证用户名"""
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")  # 获取用户名
        if not username.strip():
            return JsonResponse(
                {
                    "status": "error",
                    "msg": "用户名为空",
                },
                status=400,
            )

        if not username.isalnum():
            return JsonResponse(
                {"status": "error", "msg": "用户名不合法，不能使用特殊符号"}, status=400
            )

        if User.objects.filter(username__iexact=username.strip()).exists():
            return JsonResponse(
                {
                    "status": "error",
                    "msg": "用户名已存在",
                },
                status=400,
            )
        else:
            return JsonResponse({"status": "success", "msg": "ok"})


@csrf_exempt
def validate_email(request):
    """检验邮箱"""
    data = json.loads(request.body)
    email = data.get("email")
    if not email.strip():
        return JsonResponse(
            {
                "status": "error",
                "msg": "邮箱为空",
            },
            status=400,
        )

    try:
        ValidateEmail(email, check_deliverability=False)
    except EmailSyntaxError as e:
        return JsonResponse(
            {
                "status": "error",
                "msg": "邮箱格式不正确",
            },
            status=400,
        )
    except EmailUndeliverableError as e:
        return JsonResponse(
            {"status": "error", "msg": "该邮箱域名无法接收邮件"}, status=400
        )
    except EmailNotValidError as e:
        return JsonResponse(
            {
                "status": "error",
                "msg": "邮箱地址无效",
            },
            status=400,
        )

    if User.objects.filter(email=email).exists():
        return JsonResponse(
            {
                "status": "error",
                "msg": "该邮箱已被注册",
            },
            status=400,
        )
    else:
        return JsonResponse({"status": "success", "msg": "ok"})


def forget_password(request):
    """忘记密码"""
    if request.method == "GET":
        return render(request, "authentication/forgetpassword.html")
    elif request.method == "POST":
        email = request.POST.get("email")
        if not User.objects.filter(email=email).exists():
            context = {"error": "邮箱不存在", "email": email}
            return render(request, "authentication/forgetpassword.html", context)

        user = User.objects.get(email=email)
        current_site = get_current_site(request)  # 动态获取域名
        token = default_token_generator.make_token(user)

        link = (
            "http://"
            + current_site.domain
            + resolve_url("authentication:reset_password", user.pk, token)
        )

        content = f"""
            请点击下方链接，找回密码：
            {link}
            """
        t = Thread(
            target=send_mail,
            args=[
                "找回密码[鱿鱼账本]",  # 邮件主题
                content,  # 邮件内容
                settings.EMAIL_HOST_USER,  # 发件人
                [user.email],  # 收件人
                False,
            ],
        )
        t.start()
        return HttpResponse("请查收邮件，重置密码")


def reset_password(request, pk, token):
    if request.method == "GET":
        user = get_object_or_404(User, pk=pk)
        if not default_token_generator.check_token(user, token):
            return HttpResponseBadRequest("Invalid Token")

        messages.info(request, f"{user.username}，请设置你的新密码")
        return render(request, "authentication/reset_password.html")
    elif request.method == "POST":
        user = get_object_or_404(User, pk=pk)
        if not default_token_generator.check_token(user, token):
            return HttpResponseBadRequest("Invalid Token")

        password = request.POST.get("password")
        re_password = request.POST.get("re_password")
        if password and re_password and password != re_password:
            messages.error(request, "两次密码输入不一致")
            return render(request, "authentication/reset_password.html")

        if len(password) < 6:
            messages.error(request, "密码不能少于6位")
            return render(request, "authentication/reset_password.html")

        else:
            user.set_password(password)
            user.save()
            messages.success(request, "密码修改成功，请使用新密码进行登录！")
            return redirect(to="authentication:login")


@login_required(login_url='authentication:login')
def change_password(request):
    if request.method == 'GET':
        return render(request, 'authentication/change_password.html')

    elif request.method == 'POST':
        old_password = request.POST.get("old-password")
        new_password = request.POST.get("new-password")
        re_password = request.POST.get("re-password")

        if old_password == new_password:
            messages.error(request, '旧密码不能与新密码相同！')
            return render(request, "authentication/change_password.html")

        if not request.user.check_password(old_password):
            messages.error(request, '旧密码错误！')
            return render(request, "authentication/change_password.html")

        if len(new_password) < 6:
            messages.error(request, '密码不能少于6位')
            return render(request, "authentication/change_password.html")

        if new_password and re_password and new_password != re_password:
            messages.error(request, '两次密码输入不一致！')
            return render(request, "authentication/change_password.html")

        request.user.set_password(new_password)
        request.user.save()
        messages.success(request, '密码修改成功，请重新登录')
        return redirect(to='authentication:login')


@login_required(login_url="authentication:login")
def upload_avatar(request):
    if request.method == 'GET':
        return render(request, 'authentication/upload_avatar.html')

    elif request.method == 'POST':
        UserInfo.objects.update_or_create(
            user=request.user, defaults={"avatar": request.FILES.get("avatar")}
        )
        messages.success(request, "头像上传成功")
        return render(request, "authentication/upload_avatar.html")

from .utils import generate_verify_code


def captcha(request):
    verify_code, buff = generate_verify_code()  # 生成验证码图片和验证码字符串
    request.session["verify_code"] = (
        verify_code.lower()
    )  # 将验证码字符串存入session，方便 后续校验
    return FileResponse(
        buff, filename="verify.gif", headers={"Content-Type": "image/gif"}
    )
