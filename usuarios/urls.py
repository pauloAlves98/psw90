from django.urls import path
from . import views

urlpatterns = [
    path('', views.logar, name='index'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.logar, name='login'),
    path('logout/', views.logout, name='logout'),


]
