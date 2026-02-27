from django.shortcuts import render

def register(request):
    if request.method == 'GET':
     return render(request, 'authentication/register.html')
    
    elif request.method == 'POST':
        # 校验
        