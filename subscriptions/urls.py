from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.subscription_list, name='list'),
    path('add/', views.add_subscription, name='add'),
    path('cancel/<int:subscription_id>/', views.cancel_subscription, name='cancel'),
    path('toggle/<int:subscription_id>/', views.toggle_subscription, name='toggle'),
    
    # AJAX endpoints
    path('ajax/cities/', views.get_cities_ajax, name='get_cities_ajax'),
    path('ajax/search/', views.search_cities_ajax, name='search_cities_ajax'),
]
