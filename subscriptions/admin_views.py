from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from weather.models import City, WeatherData
from .models import Subscription, EmailLog


@staff_member_required
def admin_dashboard(request):
    """管理员仪表板"""
    
    # 用户统计
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    verified_users = User.objects.filter(is_email_verified=True).count()
    
    # 订阅统计
    total_subscriptions = Subscription.objects.count()
    active_subscriptions = Subscription.objects.filter(is_active=True).count()
    
    # 城市统计
    total_cities = City.objects.count()
    subscribed_cities = City.objects.filter(
        subscription__isnull=False
    ).distinct().count()
    
    # 邮件统计（最近30天）
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_emails = EmailLog.objects.filter(sent_at__gte=thirty_days_ago)
    total_emails = recent_emails.count()
    successful_emails = recent_emails.filter(is_sent=True).count()
    failed_emails = recent_emails.filter(is_sent=False).count()
    
    # 最近注册的用户
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # 最新的订阅
    recent_subscriptions = Subscription.objects.select_related(
        'user', 'city'
    ).order_by('-created_at')[:10]
    
    # 热门城市（订阅数最多的城市）
    popular_cities = City.objects.annotate(
        subscription_count=Count('subscription')
    ).filter(subscription_count__gt=0).order_by('-subscription_count')[:10]
    
    # 最近的邮件日志
    recent_email_logs = EmailLog.objects.select_related(
        'subscription__user', 'subscription__city'
    ).order_by('-sent_at')[:10]
    
    # 每日新增用户统计（最近7天）
    daily_user_stats = []
    for i in range(7):
        date = timezone.now().date() - timedelta(days=i)
        count = User.objects.filter(date_joined__date=date).count()
        daily_user_stats.append({
            'date': date.strftime('%m-%d'),
            'count': count
        })
    daily_user_stats.reverse()
    
    # 每日邮件发送统计（最近7天）
    daily_email_stats = []
    for i in range(7):
        date = timezone.now().date() - timedelta(days=i)
        sent_count = EmailLog.objects.filter(
            sent_at__date=date, is_sent=True
        ).count()
        failed_count = EmailLog.objects.filter(
            sent_at__date=date, is_sent=False
        ).count()
        daily_email_stats.append({
            'date': date.strftime('%m-%d'),
            'sent': sent_count,
            'failed': failed_count
        })
    daily_email_stats.reverse()
    
    context = {
        # 基础统计
        'total_users': total_users,
        'active_users': active_users,
        'verified_users': verified_users,
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'total_cities': total_cities,
        'subscribed_cities': subscribed_cities,
        
        # 邮件统计
        'total_emails': total_emails,
        'successful_emails': successful_emails,
        'failed_emails': failed_emails,
        'email_success_rate': round(successful_emails / total_emails * 100, 1) if total_emails > 0 else 0,
        
        # 列表数据
        'recent_users': recent_users,
        'recent_subscriptions': recent_subscriptions,
        'popular_cities': popular_cities,
        'recent_email_logs': recent_email_logs,
        
        # 图表数据
        'daily_user_stats': daily_user_stats,
        'daily_email_stats': daily_email_stats,
    }
    
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def user_statistics(request):
    """用户统计页面"""
    
    # 用户注册趋势（最近30天）
    user_trend = []
    for i in range(30):
        date = timezone.now().date() - timedelta(days=i)
        count = User.objects.filter(date_joined__date=date).count()
        user_trend.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    user_trend.reverse()
    
    # 用户状态分布
    user_status = {
        'active': User.objects.filter(is_active=True).count(),
        'inactive': User.objects.filter(is_active=False).count(),
        'verified': User.objects.filter(is_email_verified=True).count(),
        'unverified': User.objects.filter(is_email_verified=False).count(),
    }
    
    # 用户订阅分布
    subscription_distribution = User.objects.annotate(
        subscription_count=Count('subscription')
    ).values('subscription_count').annotate(
        user_count=Count('id')
    ).order_by('subscription_count')
    
    context = {
        'user_trend': user_trend,
        'user_status': user_status,
        'subscription_distribution': list(subscription_distribution),
    }
    
    return render(request, 'admin/user_statistics.html', context)
