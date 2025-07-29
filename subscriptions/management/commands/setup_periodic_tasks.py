from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json


class Command(BaseCommand):
    help = '设置定时任务'

    def handle(self, *args, **options):
        self.stdout.write("正在设置定时任务...")
        
        # 创建每天早上6点的定时任务
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute=0,
            hour=6,
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
            timezone='Asia/Shanghai'
        )
        
        if created:
            self.stdout.write("创建了新的定时计划: 每天早上6点")
        else:
            self.stdout.write("使用现有的定时计划: 每天早上6点")
        
        # 创建每日天气邮件发送任务
        task, created = PeriodicTask.objects.get_or_create(
            name='每日天气邮件发送',
            defaults={
                'crontab': schedule,
                'task': 'subscriptions.tasks.send_daily_weather_emails',
                'enabled': True,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS("创建了每日天气邮件发送任务")
            )
        else:
            # 更新现有任务
            task.crontab = schedule
            task.task = 'subscriptions.tasks.send_daily_weather_emails'
            task.enabled = True
            task.save()
            self.stdout.write(
                self.style.SUCCESS("更新了每日天气邮件发送任务")
            )
        
        # 创建每周清理日志的定时任务
        weekly_schedule, created = CrontabSchedule.objects.get_or_create(
            minute=0,
            hour=2,
            day_of_week=1,  # 每周一
            day_of_month='*',
            month_of_year='*',
            timezone='Asia/Shanghai'
        )
        
        cleanup_task, created = PeriodicTask.objects.get_or_create(
            name='清理旧邮件日志',
            defaults={
                'crontab': weekly_schedule,
                'task': 'subscriptions.tasks.cleanup_old_email_logs',
                'enabled': True,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS("创建了清理旧邮件日志任务")
            )
        else:
            cleanup_task.crontab = weekly_schedule
            cleanup_task.task = 'subscriptions.tasks.cleanup_old_email_logs'
            cleanup_task.enabled = True
            cleanup_task.save()
            self.stdout.write(
                self.style.SUCCESS("更新了清理旧邮件日志任务")
            )
        
        self.stdout.write(
            self.style.SUCCESS("定时任务设置完成！")
        )
        self.stdout.write("任务列表:")
        self.stdout.write("1. 每日天气邮件发送 - 每天早上6:00")
        self.stdout.write("2. 清理旧邮件日志 - 每周一凌晨2:00")
