from django.shortcuts import render,redirect



def login(request):
    return render(request, 'templates/login.html')



def forget_pwd(request):
    return render(request, 'templates/forget_pwd.html')

def dashboard(request):
    return render(request,'templates/dashboard.html')


def test(request):
    return render(request,'templates/test.html')
