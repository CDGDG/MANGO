from django.shortcuts import render

def base(request):
    return render(request, 'base.html')

def index(request):
    return render(request, 'index.html')

def elements(request):
    return render(request, 'elements.html')

def generic(request):
    return render(request, 'generic.html')
