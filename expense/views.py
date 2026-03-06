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
from django.db.models import Q
from django.http import HttpResponse, FileResponse, JsonResponse


def home(request):
    return redirect(to='expense')


@login_required(login_url='authentication:login')
def index(request):
    """支出界面首页"""
    page = request.GET.get('page', '')
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
        
    paginator = Paginator(expenses, 3)
    try:
        expenses = paginator.page(page)
    except PageNotAnInteger as e:
        expenses = paginator.page(1)
    except EmptyPage as e:
        expenses = paginator.page(paginator.num_pages)

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


def download_csv(request):
    """导出支出记录的csv文件"""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="expenses.csv"'
    # 设置 CSV 编码为 UTF-8 with BOM，防止 Excel 打开乱码
    response.write("\ufeff".encode("utf8"))
    writer = csv.writer(response)
    writer.writerow(["金额", "类型", "描述", "日期"])
    expense = Expense.objects.filter(owner=request.user).all()
    for item in expense:
        writer.writerow([item.amount, item.category, item.description, str(item.date)])
    return response


def download_excel(request):
    """导出支出记录的excel文件"""
    bio = BytesIO()
    # 创建一个新的Excel工作簿
    workbook = openpyxl.Workbook()
    # 获取活动工作表，默认是第一个工作表
    sheet = workbook.active
    # 写入表头
    sheet.append(["金额", "类型", "描述", "日期"])
    # 写入数据行
    for item in Expense.objects.filter(owner=request.user).all():
        sheet.append([item.amount, item.category, item.description, str(item.date)])
    # 将工作簿保存到BytesIO对象中
    workbook.save(bio)
    bio.seek(0)  # 将指针移动到文件开头

    response = HttpResponse(
        bio.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="expense.xlsx"'},
    )
    return response


def download_pdf(request):
    """导出支出记录的PDF"""
    bio = BytesIO()
    pdf = canvas.Canvas(bio)
    font_path = os.path.join(settings.STATICFILES_DIRS[0], "fonts", "msyh.ttc")
    pdfmetrics.registerFont(TTFont("msyh", font_path))
    pdf.setFont("msyh", 12)  # 设置字体和大小
    pdf.drawString(100, 800, "金额")
    pdf.drawString(200, 800, "类型")
    pdf.drawString(300, 800, "描述")
    pdf.drawString(400, 800, "日期")

    y = 780
    for item in Expense.objects.filter(owner=request.user).all():
        pdf.drawString(100, y, str(item.amount))
        pdf.drawString(200, y, item.category)
        pdf.drawString(300, y, item.description)
        pdf.drawString(400, y, str(item.date))
        y -= 20

    pdf.showPage()
    pdf.save()
    bio.seek(0)

    return FileResponse(bio, as_attachment=True, filename="expense.pdf")


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
