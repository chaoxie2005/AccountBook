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
from .models import Income, IncomeCategory
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count
from django.http import HttpResponse, FileResponse, JsonResponse
from accountbook.utils import get_paginated_queryset, export_to_csv, export_to_excel, export_to_pdf


@login_required(login_url='authentication:login')
def index(request):
    """收入界面首页"""
    page = request.GET.get('page', '')
    keyword = request.GET.get('keyword', '') # 搜索关键字

    if not keyword:
        incomes = Income.objects.filter(owner=request.user).order_by('-date')
    else:
        incomes = Income.objects.filter(
            Q(owner=request.user),
            Q(description__icontains=keyword)
            | Q(category__icontains=keyword)
            | Q(date__startswith=keyword),
        ).all().order_by('-date')
        
    incomes = get_paginated_queryset(incomes, request, per_page=5)

    context = {
        'incomes': incomes,
        'keyword': keyword,
    }
    return render(request, 'income/index.html', context)


@login_required(login_url='authentication:login')
def add_income(request):
    """添加收入视图"""
    context = {
        "categories": IncomeCategory.objects.all(), 
        "values": request.POST
        }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    elif request.method == 'POST':
        amount = request.POST.get('amount')
        category_name = request.POST.get('category')
        description = request.POST.get('description')
        date_str = request.POST.get('date')

        if not amount:
            messages.error(request, '金额不能为空')
            return render(request, 'income/add_income.html', context)

        if not category_name:
            messages.error(request, "类型不能为空")
            return render(request, "income/add_income.html", context)

        if not date_str:
            date_str = date.today().strftime('%Y-%m-%d')

        Income.objects.create(
            amount = amount,
            category = category_name,
            description = description,
            date = date_str,    
            owner = request.user,
        )
        messages.success(request, '收入记录添加成功')
        return redirect(to='income')


@login_required(login_url='authentication:login')
def edit_income(request, income_id):
    """编辑收入记录"""
    income = get_object_or_404(Income, owner=request.user, id=income_id)
    if request.method == 'GET':
        categories = IncomeCategory.objects.all()
        context = {
            "income": income,
            "categories": categories,
            "values": income,
        }
        return render(request, 'income/edit_income.html', context)

    elif request.method == 'POST':
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        description = request.POST.get('description')
        date_val = request.POST.get('date')

        if not amount:
            messages.error(request, '金额不能为空')
            return redirect(to='edit_income', income_id=income_id)

        if not category:
            messages.error(request, "类型不能为空")
            return redirect(to="edit_income", income_id=income_id)

        income.amount = amount
        income.category = category
        income.description = description
        if date_val:
            income.date = date_val

        income.save()
        messages.success(request, '收入记录更新成功！')
        return redirect(to='income')


@login_required(login_url='authentication:login')
def delete_income(request, income_id):
    """删除收入记录"""
    Income.objects.filter(pk=income_id, owner=request.user).delete()
    messages.success(request, "收入记录删除成功！")
    return HttpResponse('Ok')


@login_required(login_url='authentication:login')
def suggest_category(request):
    """
    智能分类：根据“描述”推荐最可能的收入分类。

    返回格式：
    - category: 推荐的分类名称（必须存在于 IncomeCategory 表中，否则返回空字符串）
    - confidence: 置信度（0~1，数值越大越可靠）
    - source: 推荐来源（history | keyword | 空）
    """
    q = (request.GET.get("q") or "").strip()
    # 输入太短时不做推荐，避免误判
    if len(q) < 2:
        return JsonResponse({"category": "", "confidence": 0, "source": ""})

    # 仅允许返回“已有分类”，防止选中不存在的分类导致表单校验/展示异常
    available_categories = set(IncomeCategory.objects.values_list("name", flat=True))

    def pick_from_history(text):
        # 历史优先：从用户自己的历史收入记录中找“相似描述”的最常用分类
        # n 越大，表示匹配的前缀越长，通常越准确
        for n in (6, 4, 3, 2):
            key = text[:n]
            if len(key) < 2:
                continue
            rows = (
                Income.objects.filter(owner=request.user, description__icontains=key)
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
        keyword_map = [
            (("工资", "薪资", "薪水", "发薪", "salary"), "工资"),
            (("奖金", "年终", "绩效", "补贴", "提成"), "奖金"),
            (("利息", "分红", "理财", "基金", "股票", "收益"), "理财收益"),
            (("退款", "返现", "报销", "赔付", "红包"), "其他收入"),
        ]
        for keywords, category in keyword_map:
            if category not in available_categories:
                continue
            for kw in keywords:
                if kw.lower() in text.lower():
                    return category, 0.7
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


@login_required(login_url='authentication:login')
def index_stats(request):
    """
    首页的echarts图形
    """
    today = date.today()
    start_date = today.replace(month=1, day=1) # 本年的第一天
    end_date = today.replace(month=12, day=31) # 本月最后一天
    incomes = Income.objects.filter(
        owner=request.user, date__gte=start_date, date__lte=end_date
    ).all()
    category_dict = defaultdict(float)
    monthly_dict = defaultdict(float)
    for item in incomes:
        category_dict[item.category] += item.amount
        month = item.date.strftime('%Y-%m')
        monthly_dict[month] += item.amount

    sorted_months = sorted(monthly_dict.keys())

    datalist = {
        "category": [{"name": k, "value": v} for k, v in category_dict.items()],
        "month": {
            "key": sorted_months,
            "value": [monthly_dict[key] for key in sorted_months],
        } 
    }
    return JsonResponse(datalist)


@login_required(login_url='authentication:login')
def income_summary_stats(request):
    """
    收入统计页面
    """
    today = date.today()
    start_date = today.replace(year=today.year - 1, month=1, day=1)

    today_sum_stats = {"title": "今日收入", "count": 0, "sum": 0}
    this_month_sum_stats = {"title": "本月收入", "count": 0, "sum": 0}
    this_year_sum_stats = {"title": "今年收入", "count": 0, "sum": 0}
    last_year_stats = {"title": "去年收入", "count": 0, "sum": 0}

    incomes = Income.objects.filter(owner=request.user, date__gte=start_date).all()
    for item in incomes:
        if item.date == today:
            today_sum_stats['count'] += 1
            today_sum_stats['sum'] += item.amount
        elif item.date >= today.replace(day=1):
            this_month_sum_stats['count'] += 1
            this_month_sum_stats['sum'] += item.amount
        elif item.date >= today.replace(month=1, day=1):
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
    return render(request, "income/income_summary_stats.html", context)


@login_required(login_url='authentication:login')
def income_s1(request):
    """今年各类型收入占比 饼图"""
    incomes = Income.objects.filter(
        owner=request.user, date__year=date.today().year
    ).all()
    category_dict = defaultdict(float)
    for item in incomes:
        category_dict[item.category] += item.amount
    response_data = [{"name": k, "value": v} for k, v in category_dict.items()]
    return JsonResponse(response_data, safe=False)


@login_required(login_url='authentication:login')
def income_s2(request):
    """今年各类型收入金额，柱状图"""
    incomes = Income.objects.filter(owner=request.user, date__year=date.today().year)
    category_dict = defaultdict(float)
    for item in incomes:
        category_dict[item.category] += item.amount

    data = {
        "captions": list(category_dict.keys()),
        "values": [category_dict[key] for key in category_dict],
    }
    return JsonResponse(data)


@login_required(login_url='authentication:login')
def income_s3(request):
    """今年每月收入金额，折线图"""
    incomes = Income.objects.filter(owner=request.user, date__year=date.today().year)
    month_incomes = {str(m + 1): 0 for m in range(12)}
    for item in incomes:
        month_incomes[str(item.date.month)] += item.amount

    values = [month_incomes[m] for m in month_incomes]
    max_value_index = values.index(max(values)) if values else 0
    data = {
        "captions": list(month_incomes.keys()),
        "values": values,
        "max_value_index": max_value_index,
    }
    return JsonResponse(data)


@login_required(login_url='authentication:login')
def income_s4(request, year):
    """年度累计收入金额，折线图"""
    incomes = Income.objects.filter(owner=request.user, date__year=year).all()
    month_incomes = {str(m + 1): 0 for m in range(12)}
    for item in incomes:
        m = item.date.month
        for k in month_incomes.keys():
            if int(k) >= m:
                month_incomes[k] += item.amount
    data = {
        "captions": list(month_incomes.keys()),
        "values": [month_incomes[k] for k in month_incomes],
    }
    return JsonResponse(data)



@login_required(login_url='authentication:login')
def download_csv(request):
    """导出收入记录的csv文件"""
    incomes = Income.objects.filter(owner=request.user).all()
    headers = ["金额", "类型", "描述", "日期"]
    data_func = lambda item: [item.amount, item.category, item.description, str(item.date)]
    return export_to_csv(incomes, "incomes", headers, data_func)


@login_required(login_url='authentication:login')
def download_excel(request):
    """导出收入记录的excel文件"""
    incomes = Income.objects.filter(owner=request.user).all()
    headers = ["金额", "类型", "描述", "日期"]
    data_func = lambda item: [item.amount, item.category, item.description, str(item.date)]
    return export_to_excel(incomes, "income", headers, data_func)


@login_required(login_url='authentication:login')
def download_pdf(request):
    """导出收入记录的PDF"""
    incomes = Income.objects.filter(owner=request.user).all()
    headers = ["金额", "类型", "描述", "日期"]
    data_func = lambda item: [item.amount, item.category, item.description, str(item.date)]
    return export_to_pdf(incomes, "income", headers, data_func)
