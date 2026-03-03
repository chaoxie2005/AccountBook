from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Expense, Category
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

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
