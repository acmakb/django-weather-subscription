#!/usr/bin/env python3
"""
测试邮件发送任务脚本
使用方法: python test_email_task.py
"""

import os
import sys
import django
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weatherblog.settings')
django.setup()

def test_celery_connection():
    """测试Celery连接"""
    try:
        from celery import current_app
        
        # 检查Celery配置
        print("🔍 Celery配置检查:")
        print(f"   Broker URL: {current_app.conf.broker_url}")
        print(f"   Result Backend: {current_app.conf.result_backend}")
        
        # 测试Celery连接
        inspect = current_app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            print("✅ Celery Worker连接成功")
            for worker, stat in stats.items():
                print(f"   Worker: {worker}")
                print(f"   进程数: {stat.get('pool', {}).get('max-concurrency', 'N/A')}")
            return True
        else:
            print("❌ 无法连接到Celery Worker")
            print("   请确保Celery Worker正在运行")
            return False
            
    except Exception as e:
        print(f"❌ Celery连接测试失败: {e}")
        return False

def test_redis_connection():
    """测试Redis连接"""
    try:
        import redis
        from django.conf import settings
        
        # 解析Redis URL
        broker_url = settings.CELERY_BROKER_URL
        print(f"🔍 Redis连接测试: {broker_url}")
        
        # 创建Redis连接
        r = redis.from_url(broker_url)
        
        # 测试连接
        response = r.ping()
        if response:
            print("✅ Redis连接成功")
            
            # 获取Redis信息
            info = r.info()
            print(f"   Redis版本: {info.get('redis_version', 'N/A')}")
            print(f"   连接数: {info.get('connected_clients', 'N/A')}")
            return True
        else:
            print("❌ Redis连接失败")
            return False
            
    except Exception as e:
        print(f"❌ Redis连接测试失败: {e}")
        return False

def test_email_settings():
    """测试邮件配置"""
    try:
        from django.conf import settings
        from django.core.mail import send_mail
        
        print("🔍 邮件配置检查:")
        print(f"   邮件后端: {settings.EMAIL_BACKEND}")
        print(f"   SMTP主机: {settings.EMAIL_HOST}")
        print(f"   SMTP端口: {settings.EMAIL_PORT}")
        print(f"   使用TLS: {settings.EMAIL_USE_TLS}")
        print(f"   发件人: {settings.EMAIL_HOST_USER}")
        
        # 测试邮件发送
        print("\n📧 测试邮件发送...")
        
        test_subject = f"天气订阅系统测试邮件 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        test_message = """
这是一封测试邮件，用于验证天气订阅系统的邮件发送功能。

如果您收到这封邮件，说明邮件配置正确。

发送时间: {time}
系统状态: 正常运行
        """.format(time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # 发送测试邮件
        send_mail(
            subject=test_subject,
            message=test_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],  # 发送给自己
            fail_silently=False,
        )
        
        print("✅ 测试邮件发送成功")
        print(f"   收件人: {settings.EMAIL_HOST_USER}")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送测试失败: {e}")
        return False

def test_celery_task():
    """测试Celery任务"""
    try:
        from subscriptions.tasks import test_celery_task, send_daily_weather_emails
        
        print("🔍 Celery任务测试:")
        
        # 测试简单任务
        print("   执行测试任务...")
        result = test_celery_task.delay()
        
        # 等待结果
        try:
            task_result = result.get(timeout=10)
            print(f"✅ 测试任务执行成功: {task_result}")
        except Exception as e:
            print(f"❌ 测试任务执行失败: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Celery任务测试失败: {e}")
        return False

def test_weather_email_task():
    """测试天气邮件任务"""
    try:
        from subscriptions.tasks import send_daily_weather_emails
        from subscriptions.models import Subscription
        
        print("🔍 天气邮件任务测试:")
        
        # 检查订阅数量
        active_subscriptions = Subscription.objects.filter(is_active=True)
        print(f"   活跃订阅数量: {active_subscriptions.count()}")
        
        if active_subscriptions.count() == 0:
            print("⚠️  没有活跃的订阅，无法测试邮件发送")
            return True
        
        # 显示订阅详情
        for sub in active_subscriptions[:3]:  # 只显示前3个
            print(f"   - {sub.user.email} -> {sub.city.name}")
        
        if active_subscriptions.count() > 3:
            print(f"   ... 还有 {active_subscriptions.count() - 3} 个订阅")
        
        # 执行邮件发送任务
        print("\n📧 执行天气邮件发送任务...")
        result = send_daily_weather_emails.delay()
        
        try:
            task_result = result.get(timeout=30)
            print(f"✅ 天气邮件任务执行成功: {task_result}")
            return True
        except Exception as e:
            print(f"❌ 天气邮件任务执行失败: {e}")
            return False
        
    except Exception as e:
        print(f"❌ 天气邮件任务测试失败: {e}")
        return False

def check_periodic_tasks():
    """检查定时任务配置"""
    try:
        from django_celery_beat.models import PeriodicTask, CrontabSchedule
        
        print("🔍 定时任务配置检查:")
        
        # 检查定时任务
        tasks = PeriodicTask.objects.filter(enabled=True)
        print(f"   启用的定时任务数量: {tasks.count()}")
        
        for task in tasks:
            print(f"   - {task.name}")
            print(f"     任务: {task.task}")
            if task.crontab:
                cron = task.crontab
                print(f"     计划: {cron.minute}:{cron.hour} {cron.day_of_week} {cron.day_of_month} {cron.month_of_year}")
            print(f"     启用: {task.enabled}")
            print(f"     最后运行: {task.last_run_at or '从未运行'}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 定时任务检查失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🧪 天气订阅系统邮件功能测试")
    print("=" * 60)
    
    success_count = 0
    total_tests = 6
    
    # 测试1: Redis连接
    if test_redis_connection():
        success_count += 1
    print()
    
    # 测试2: Celery连接
    if test_celery_connection():
        success_count += 1
    print()
    
    # 测试3: 邮件配置
    if test_email_settings():
        success_count += 1
    print()
    
    # 测试4: Celery任务
    if test_celery_task():
        success_count += 1
    print()
    
    # 测试5: 定时任务配置
    if check_periodic_tasks():
        success_count += 1
    print()
    
    # 测试6: 天气邮件任务
    if test_weather_email_task():
        success_count += 1
    print()
    
    print("=" * 60)
    print(f"📊 测试结果: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！邮件功能配置正确")
        print("\n📝 下一步:")
        print("   1. 确保所有服务正在运行: ./check_status.sh")
        print("   2. 等待明天早上6点自动发送邮件")
        print("   3. 或者手动触发任务测试")
    else:
        print("⚠️  部分测试失败，请检查配置")
        print("\n🔧 修复建议:")
        print("   1. 检查Redis服务: sudo systemctl status redis")
        print("   2. 检查Celery服务: ./check_status.sh")
        print("   3. 检查邮件配置: 确认QQ邮箱授权码")
        
    print("=" * 60)

if __name__ == "__main__":
    main()
