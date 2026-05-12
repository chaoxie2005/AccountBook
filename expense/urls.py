from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="expense"),  # 支出首页
    path("add_expense/", views.add_expense, name="add_expense"),  # 添加数据路由
    path(
        "edit_expense/<int:expense_id>", views.edit_expense, name="edit_expense"
    ),  # 编辑支出路由
    path(
        "delete_expense/<int:expense_id>", views.delete_expense, name="delete_expense"
    ),  # 删除路由
    path("download_csv/", views.download_csv, name="download_csv"),  # 导出csv
    path("download_excel/", views.download_excel, name="download_excel"),  # 导出excel
    path("download_pdf/", views.download_pdf, name="download_pdf"),  # 导出PDF
    # 智能分类：根据描述推荐分类（前端输入描述时调用）
    path("suggest-category/", views.suggest_category, name="expense_suggest_category"),
    path("index_stats/", views.index_stats, name="index_stats"),
    path(
        "expense_summary_stats/",
        views.expense_summary_stats,
        name="expense_summary_stats",
    ),  # 支出汇总页面
    path("expense_s1/", views.expense_s1, name="expense-s1"),  # 支出汇总视图
    path("expense_s2/", views.expense_s2, name="expense-s2"),  # 支出汇总视图
    path("expense_s3/", views.expense_s3, name="expense-s3"),  # 支出汇总视图
    path("expense_s4/<int:year>/", views.expense_s4, name="expense-s4"),  # 支出汇总视图
]
