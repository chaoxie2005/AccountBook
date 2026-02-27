from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='expense'), # 支出首页
]
