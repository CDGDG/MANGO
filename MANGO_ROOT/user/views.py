from django.shortcuts import render

def base(request):
    return render(request, 'base.html')

def index(request):
    return render(request, 'index.html')

def elements(request):
    return render(request, 'elements.html')

def generic(request):
    return render(request, 'generic.html')

def likesinger(request):
    return render(request, 'likesinger.html')

def likesong(request):
    return render(request, 'likesong.html')

def myinfo(reqeust):
    pass

def login(request):
    return render(request, 'login.html')