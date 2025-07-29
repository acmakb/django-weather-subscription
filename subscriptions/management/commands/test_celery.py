from django.core.management.base import BaseCommand
from subscriptions.tasks import test_celery_task, send_daily_weather_emails


class Command(BaseCommand):
    help = '测试Celery任务'

    def add_arguments(self, parser):
        parser.add_argument(
            '--task',
            type=str,
            choices=['test', 'weather'],
            default='test',
            help='要测试的任务类型'
        )

    def handle(self, *args, **options):
        task_type = options['task']
        
        if task_type == 'test':
            self.stdout.write("正在测试Celery基本功能...")
            
            # 异步执行测试任务
            result = test_celery_task.delay()
            
            self.stdout.write(f"任务ID: {result.id}")
            self.stdout.write("等待任务完成...")
            
            try:
                # 等待任务完成（最多30秒）
                task_result = result.get(timeout=30)
                self.stdout.write(
                    self.style.SUCCESS(f"任务完成: {task_result}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"任务执行失败: {str(e)}")
                )
        
        elif task_type == 'weather':
            self.stdout.write("正在测试天气邮件发送任务...")
            
            # 异步执行天气邮件发送任务
            result = send_daily_weather_emails.delay()
            
            self.stdout.write(f"任务ID: {result.id}")
            self.stdout.write("等待任务完成...")
            
            try:
                # 等待任务完成（最多60秒）
                task_result = result.get(timeout=60)
                self.stdout.write(
                    self.style.SUCCESS(f"任务完成: {task_result}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"任务执行失败: {str(e)}")
                )
