from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    return redirect(to='expense')


@login_required(login_url='authentication:login')
def index(request):
    return render(request, 'expense/index.html')