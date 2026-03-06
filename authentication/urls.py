from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path("register/", views.register, name="register"),  # 注册路由
    path("login/", views.login, name="login"),  # 登录路由
    path("logout/", views.logout, name="logout"),  # 退出登录路由
    path(
        "validate_username/", views.validate_username, name="validate_username"
    ),  # 实时验证用户名
    path(
        "validate_email/", views.validate_email, name="validate_email"
    ),  # 实时验证邮箱
    path('verify_account/<str:username>/', views.verify_account, name='verify_account'), # 激活账号
    path('forget_password/', views.forget_password, name='forget_password'), # 进入到忘记密码界面
    path('reset_password/<int:pk>/<str:token>', views.reset_password, name='reset_password'), # 真正重置密码的逻辑
    path('change_password/', views.change_password, name='change_password'), # 修改密码路由
]
