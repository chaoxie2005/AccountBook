from django.shortcuts import render, redirect

def home(request):
    return redirect(to='expense')


def index(request):
    return render(request, 'expense/index.html')