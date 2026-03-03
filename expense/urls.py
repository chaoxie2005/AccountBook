from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='expense'), # 支出首页
    path('add_expense/', views.add_expense, name='add_expense') # 添加数据路由
]
