from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from weather.models import City
from .models import Subscription
from .forms import SubscriptionForm, CitySearchForm


@login_required
def subscription_list(request):
    """订阅列表视图"""
    subscriptions = Subscription.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'subscriptions/list.html', {
        'subscriptions': subscriptions
    })


@login_required
def add_subscription(request):
    """添加订阅视图"""
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            final_city = form.cleaned_data['final_city']
            email = form.cleaned_data['email']

            # 检查是否已经订阅过该城市
            if Subscription.objects.filter(user=request.user, city=final_city).exists():
                messages.error(request, f'您已经订阅过 {final_city.get_full_name()} 的天气信息')
            else:
                subscription = form.save(commit=False)
                subscription.user = request.user
                subscription.city = final_city
                subscription.save()

                messages.success(request, f'成功订阅 {final_city.get_full_name()} 的天气信息')
                return redirect('subscriptions:list')
    else:
        form = SubscriptionForm()

    return render(request, 'subscriptions/add.html', {'form': form})


@login_required
def cancel_subscription(request, subscription_id):
    """取消订阅视图"""
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)

    if request.method == 'POST':
        city_name = subscription.city.get_full_name()
        subscription.delete()
        messages.success(request, f'已取消订阅 {city_name} 的天气信息')
        return redirect('subscriptions:list')

    return render(request, 'subscriptions/cancel.html', {'subscription': subscription})


@login_required
def toggle_subscription(request, subscription_id):
    """切换订阅状态"""
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
    subscription.is_active = not subscription.is_active
    subscription.save()

    status = "激活" if subscription.is_active else "暂停"
    messages.success(request, f'已{status} {subscription.city.get_full_name()} 的天气订阅')
    return redirect('subscriptions:list')


def get_cities_ajax(request):
    """AJAX获取城市列表"""
    parent_id = request.GET.get('parent_id')
    level = request.GET.get('level')

    if parent_id and level:
        cities = City.objects.filter(
            parent_id=parent_id,
            level=int(level)
        ).order_by('name')

        data = [{'id': city.id, 'name': city.name} for city in cities]
        return JsonResponse({'cities': data})

    return JsonResponse({'cities': []})


def search_cities_ajax(request):
    """AJAX搜索城市"""
    query = request.GET.get('q', '').strip()

    if len(query) >= 2:
        cities = City.objects.filter(
            Q(name__icontains=query) & Q(level__gte=2)  # 只搜索市级以上
        ).select_related('parent')[:20]

        data = []
        for city in cities:
            data.append({
                'id': city.id,
                'name': city.name,
                'full_name': city.get_full_name(),
                'adcode': city.adcode
            })

        return JsonResponse({'cities': data})

    return JsonResponse({'cities': []})
