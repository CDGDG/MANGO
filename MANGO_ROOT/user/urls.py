"""MANGO URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

app_name = 'User'

urlpatterns = [
    path('base/', views.base, name='base'),
    path('index/', views.index, name='index'),
    path('elements/', views.elements, name='elements'),
    path('generic/', views.generic, name='generic'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('join/', views.join, name='join'),
    path('checkid/', views.checkid, name='checkid'),
    path('addPlaylist/', views.addPlaylist, name='addPlaylist'),
    path('getPlaylist/', views.getPlaylist, name='getPlaylist'),
    path('showPlaylist/', views.showPlaylist, name='showPlaylist'),
    path('deletePlaylist/<track>/', views.deletePlaylist, name='deletePlaylist'),
]
