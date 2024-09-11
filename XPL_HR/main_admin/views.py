from django.shortcuts import render,redirect



def login(request):
    return render(request, 'templates/login.html')
