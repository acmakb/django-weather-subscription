from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from subscriptions.models import Subscription
from .services import WeatherService


def home_view(request):
    """首页视图"""
    if request.user.is_authenticated:
        return dashboard_view(request)
    return render(request, 'weather/home.html')


@login_required
def dashboard_view(request):
    """用户仪表板"""
    # 获取用户的订阅
    subscriptions = Subscription.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('city')

    # 获取天气数据
    weather_service = WeatherService()
    weather_data = []

    for subscription in subscriptions[:6]:  # 最多显示6个城市的天气
        weather_info = weather_service.get_weather_for_email(subscription.city.adcode)
        if weather_info:
            weather_data.append({
                'subscription': subscription,
                'weather': weather_info
            })

    context = {
        'subscriptions': subscriptions,
        'weather_data': weather_data,
        'total_subscriptions': subscriptions.count()
    }

    return render(request, 'weather/dashboard.html', context)
