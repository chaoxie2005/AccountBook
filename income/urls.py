from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='income'),
    path('add-income/', views.add_income, name='add_income'),
    path('edit-income/<int:income_id>/', views.edit_income, name='edit_income'),
    path('delete-income/<int:income_id>/', views.delete_income, name='delete_income'),
    path('download-csv/', views.download_csv, name='download_income_csv'),
    path('download-excel/', views.download_excel, name='download_income_excel'),
    path('download-pdf/', views.download_pdf, name='download_income_pdf'),
    # 智能分类：根据描述推荐分类（前端输入描述时调用）
    path('suggest-category/', views.suggest_category, name='income_suggest_category'),
    path('index_stats/', views.index_stats, name='income_index_stats'),
    path('income_summary_stats/', views.income_summary_stats, name='income_summary_stats'),
    path('income_s1/', views.income_s1, name='income-s1'),
    path('income_s2/', views.income_s2, name='income-s2'),
    path('income_s3/', views.income_s3, name='income-s3'),
    path('income_s4/<int:year>/', views.income_s4, name='income-s4'),
]
