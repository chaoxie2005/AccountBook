import csv
import openpyxl
from io import BytesIO
from django.conf import settings
import os
from datetime import date, datetime
from collections import defaultdict
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Expense, Category
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count
from django.http import HttpResponse, FileResponse, JsonResponse


def home(request):
    return redirect(to='expense')


from accountbook.utils import get_paginated_queryset, export_to_csv, export_to_excel, export_to_pdf


@login_required(login_url='authentication:login')
def index(request):
    """支出界面首页"""
    keyword = request.GET.get('keyword', '') # 搜索关键字

    if not keyword:
        expenses = Expense.objects.filter(owner=request.user)
    else:
        expenses = Expense.objects.filter(
            Q(owner=request.user),
            Q(description__icontains=keyword)
            | Q(category__icontains=keyword)
            | Q(date__startswith=keyword),
        ).all().order_by('-date')
        
    expenses = get_paginated_queryset(expenses, request, per_page=3)

    context = {
        'expenses': expenses,
        'keyword': keyword,
    }
    return render(request, 'expense/index.html', context)


def add_expense(request):
    """添加支出视图"""
    context = {
        "categories": Category.objects.all(), 
        "values": request.POST
        }
    if request.method == 'GET':
        return render(request, 'expense/add_expense.html', context)

    elif request.method == 'POST':
        amount = request.POST.get('amount')
        category_name = request.POST.get('category')

        if not amount:
            messages.error(request, '金额不能为空')
            return render(request, 'expense/add_expense.html', context)

        if not category_name:
            messages.error(request, "类型不能为空")
            return render(request, "expense/add_expense.html", context)

        Expense.objects.create(
            amount = amount,
            category = category_name,
            description = request.POST.get('description'),
            date = request.POST.get('date'),    
            owner = request.user,
        )
        messages.success(request, '支出记录添加成功')
        return redirect(to='expense')


def edit_expense(request, expense_id):
    """编辑支出记录"""
    expense = get_object_or_404(Expense, owner=request.user, id=expense_id)
    if request.method == 'GET':
        categories = Category.objects.all()
        context = {
            "expense": expense,
            "categories": categories,
            "values": expense,
        }
        return render(request, 'expense/edit_expense.html', context)

    elif request.method == 'POST':
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        description = request.POST.get('description')
        date = request.POST.get('date')

        if not expense:
            messages.error(request, '未找到该支出记录！')
            return redirect(to='expense')

        if not amount:
            messages.error(request, '金额不能为空')
            return redirect(to='edit_expense', expense_id=expense_id)

        if not category:
            messages.error(request, "类型不能为空")
            return redirect(to="edit_expense", expense_id=expense_id)

        expense.amount = amount
        expense.category = category
        expense.description = description
        if date:
            expense.date = date
        else:
            expense.date = expense.date # 保持原日期不变

        expense.save()
        messages.success(request, '支出记录更新成功！')
        return redirect(to='expense')


def delete_expense(request, expense_id):
    """删除支出记录"""
    Expense.objects.filter(pk=expense_id, owner=request.user).delete()
    messages.success(request, "支出记录删除成功！")
    return HttpResponse('Ok')


@login_required(login_url='authentication:login')
def suggest_category(request):
    """
    智能分类：根据“描述”推荐最可能的支出分类。

    返回格式：
    - category: 推荐的分类名称（必须存在于 Category 表中，否则返回空字符串）
    - confidence: 置信度（0~1，数值越大越可靠）
    - source: 推荐来源（history | keyword | 空）
    """
    q = (request.GET.get("q") or "").strip()
    # 输入太短时不做推荐，避免误判
    if len(q) < 2:
        return JsonResponse({"category": "", "confidence": 0, "source": ""})

    # 仅允许返回“已有分类”，防止选中不存在的分类导致表单校验/展示异常
    available_categories = set(Category.objects.values_list("name", flat=True))

    def pick_from_history(text):
        # 历史优先：从用户自己的历史支出记录中找“相似描述”的最常用分类
        # n 越大，表示匹配的前缀越长，通常越准确
        for n in (6, 4, 3, 2):
            key = text[:n]
            if len(key) < 2:
                continue
            rows = (
                Expense.objects.filter(owner=request.user, description__icontains=key)
                .values("category")
                .annotate(cnt=Count("id"))
                .order_by("-cnt")
            )
            for row in rows:
                cat = row.get("category") or ""
                if cat in available_categories:
                    # 前缀越长，置信度给得越高
                    confidence = 0.9 if n >= 4 else 0.8
                    return cat, confidence
        return "", 0

    def pick_from_keywords(text):
        # 关键词兜底：当历史匹配不到时，使用关键词规则做推荐
        # 注意：不同人自定义的分类名称可能不同，所以用“候选分类列表”来兼容
        keyword_rules = [
            (
                ("外卖", "早餐", "午餐", "晚餐", "餐", "奶茶", "咖啡", "饭", "火锅", "烧烤"),
                ("餐饮", "饮食", "吃饭", "餐费", "食物", "食品"),
            ),
            (
                ("地铁", "公交", "打车", "滴滴", "高铁", "火车", "机票", "停车", "油", "加油"),
                ("交通", "出行", "通勤"),
            ),
            (
                ("房租", "租房", "物业", "水费", "电费", "燃气", "宽带", "网费"),
                ("居住", "房租", "生活缴费", "水电"),
            ),
            (
                ("淘宝", "京东", "拼多多", "购物", "衣", "鞋", "包", "超市"),
                ("购物", "日用", "生活用品", "超市"),
            ),
            (
                ("药", "医院", "挂号", "体检", "医保", "牙", "口腔"),
                ("医疗", "健康", "医药"),
            ),
            (
                ("电影", "游戏", "KTV", "演出", "旅游", "景区", "酒店"),
                ("娱乐", "旅行", "旅游"),
            ),
            (
                ("书", "课程", "培训", "学习", "考试", "资料"),
                ("学习", "教育", "培训"),
            ),
        ]

        for keywords, candidates in keyword_rules:
            if not any(kw in text for kw in keywords):
                continue
            for candidate in candidates:
                if candidate in available_categories:
                    return candidate, 0.7
        return "", 0

    # 1) 优先用历史匹配
    category, confidence = pick_from_history(q)
    if category:
        return JsonResponse({"category": category, "confidence": confidence, "source": "history"})

    # 2) 其次用关键词规则
    category, confidence = pick_from_keywords(q)
    if category:
        return JsonResponse({"category": category, "confidence": confidence, "source": "keyword"})

    # 3) 都匹配不到则不推荐
    return JsonResponse({"category": "", "confidence": 0, "source": ""})


def download_csv(request):
    """导出支出记录的csv文件"""
    expenses = Expense.objects.filter(owner=request.user).all()
    headers = ["金额", "类型", "描述", "日期"]
    data_func = lambda item: [item.amount, item.category, item.description, str(item.date)]
    return export_to_csv(expenses, "expenses", headers, data_func)


def download_excel(request):
    """导出支出记录的excel文件"""
    expenses = Expense.objects.filter(owner=request.user).all()
    headers = ["金额", "类型", "描述", "日期"]
    data_func = lambda item: [item.amount, item.category, item.description, str(item.date)]
    return export_to_excel(expenses, "expense", headers, data_func)


def download_pdf(request):
    """导出支出记录的PDF"""
    expenses = Expense.objects.filter(owner=request.user).all()
    headers = ["金额", "类型", "描述", "日期"]
    data_func = lambda item: [item.amount, item.category, item.description, str(item.date)]
    return export_to_pdf(expenses, "expense", headers, data_func)


def index_stats(request):
    """
    首页的echarts图形
    饼图所需数据格式：[{}]
    柱形图所需数据格式：[]
    """
    today = date.today()
    start_date = today.replace(month=1, day=1) # 本年的第一天
    end_date = today.replace(month=12, day=31) # 本月最后一天
    expense = Expense.objects.filter(
        owner=request.user, date__gte=start_date, date__lte=end_date
    ).all()
    category_dict = defaultdict(float)  # 统计类型字典
    monthly_dict = defaultdict(float) # 统计月份字典
    for item in expense:
        category_dict[item.category] += item.amount  # 统计每个类型的总金额

        month = item.date.strftime('%Y-%m')
        monthly_dict[month] += item.amount # 统计每个月份的总金额

    # 对月份进行排序，确保图表X轴有序
    sorted_months = sorted(monthly_dict.keys())

    datalist = {
        "category": [{"name": k, "value": v} for k, v in category_dict.items()],
        "month": {
            "key": sorted_months,
            "value": [monthly_dict[key] for key in sorted_months],
        } 
    }
    return JsonResponse(datalist)


def expense_summary_stats(request):
    """
    支出统计页面，展示今日、本月、今年、去年等不同时间范围的支出总金额和记录数
    """
    today = date.today()
    start_date = today.replace(year=today.year - 1, month=1, day=1)  # 一年前的第一天

    today_sum_stats = {"title": "今日支出", "count": 0, "sum": 0}
    this_month_sum_stats = {"title": "本月支出", "count": 0, "sum": 0}
    this_year_sum_stats = {"title": "今年支出", "count": 0, "sum": 0}
    last_year_stats = {"title": "去年支出", "count": 0, "sum": 0}

    expense = Expense.objects.filter(owner=request.user, date__gte=start_date).all()
    for item in expense:
        if item.date == today: # 今日支出
            today_sum_stats['count'] += 1
            today_sum_stats['sum'] += item.amount
        elif item.date >= today.replace(day=1): # 本月支出
            this_month_sum_stats['count'] += 1
            this_month_sum_stats['sum'] += item.amount
        elif item.date >= today.replace(month=1, day=1): # 今年支出
            this_year_sum_stats['count'] += 1
            this_year_sum_stats['sum'] += item.amount
        else:
            last_year_stats['count'] += 1
            last_year_stats['sum'] += item.amount
    
    context = {
        'sum_stats_list': [
            today_sum_stats,
            this_month_sum_stats,
            this_year_sum_stats,
            last_year_stats,
        ]
    }
    return render(request, "expense/expense_summary_stats.html", context)


def expense_s1(request):
    """今年各类型支出占比 饼图 数据接口"""
    expenses = Expense.objects.filter(
        owner=request.user, date__year=date.today().year
    ).all()
    category_dict = defaultdict(float)
    for item in expenses:
        category_dict[item.category] += item.amount  # 将金额累加到对应类型的总金额中
    category_list = sorted(category_dict.keys())  # 按类型名称排序
    response_data = [{"name": k, "value": v} for k, v in category_dict.items()]
    return JsonResponse(response_data, safe=False)


def expense_s2(request):
    """今年各类型支出金额，柱状图"""
    expenses = Expense.objects.filter(owner=request.user, date__year=date.today().year)
    category_dict = defaultdict(float)
    for item in expenses:
        category_dict[item.category] += item.amount

    data = {
        "captions": list(category_dict.keys()),
        "values": [category_dict[key] for key in category_dict],
    }

    return JsonResponse(data)


def expense_s3(request):
    """今年每月支出金额，折线图"""
    expenses = Expense.objects.filter(owner=request.user, date__year=date.today().year)

    month_expenses = {str(m + 1): 0 for m in range(12)}
    for item in expenses:
        month_expenses[str(item.date.month)] += item.amount

    values = [month_expenses[m] for m in month_expenses]
    max_value_index = values.index(max(values))
    data = {
        "captions": list(month_expenses.keys()),
        "values": values,
        "max_value_index": max_value_index,
    }
    return JsonResponse(data)


def expense_s4(request, year):
    """年度累计支出金额，折线图"""
    expenses = Expense.objects.filter(owner=request.user, date__year=year).all()

    month_expenses = {str(m + 1): 0 for m in range(12)}
    for item in expenses:
        m = item.date.month
        for k in month_expenses.keys():
            if int(k) >= m:
                month_expenses[k] += item.amount
    data = {
        "captions": list(month_expenses.keys()),
        "values": [month_expenses[k] for k in month_expenses],
    }
    return JsonResponse(data)
