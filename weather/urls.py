from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
