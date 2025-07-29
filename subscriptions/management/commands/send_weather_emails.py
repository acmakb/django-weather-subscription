from django.core.management.base import BaseCommand
from subscriptions.models import Subscription
from subscriptions.email_service import EmailService


class Command(BaseCommand):
    help = '手动发送天气邮件'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='指定用户ID，只发送该用户的订阅邮件'
        )
        parser.add_argument(
            '--subscription-id',
            type=int,
            help='指定订阅ID，只发送该订阅的邮件'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示将要发送的邮件，不实际发送'
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        subscription_id = options.get('subscription_id')
        dry_run = options.get('dry_run')
        
        # 构建查询条件
        queryset = Subscription.objects.filter(is_active=True)
        
        if subscription_id:
            queryset = queryset.filter(id=subscription_id)
        elif user_id:
            queryset = queryset.filter(user_id=user_id)
        
        subscriptions = queryset.select_related('user', 'city')
        
        if not subscriptions.exists():
            self.stdout.write(
                self.style.WARNING('没有找到符合条件的活跃订阅')
            )
            return
        
        self.stdout.write(f"找到 {subscriptions.count()} 个活跃订阅")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("这是预演模式，不会实际发送邮件"))
            for subscription in subscriptions:
                self.stdout.write(
                    f"  - {subscription.user.username} ({subscription.email}) "
                    f"订阅了 {subscription.city.get_full_name()}"
                )
            return
        
        # 实际发送邮件
        email_service = EmailService()
        success_count = 0
        failure_count = 0
        
        for subscription in subscriptions:
            self.stdout.write(
                f"正在发送邮件给 {subscription.email} "
                f"({subscription.city.get_full_name()})..."
            )
            
            if email_service.send_weather_email(subscription):
                success_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ 发送成功")
                )
            else:
                failure_count += 1
                self.stdout.write(
                    self.style.ERROR(f"  ✗ 发送失败")
                )
        
        # 显示总结
        self.stdout.write("\n" + "="*50)
        self.stdout.write(f"邮件发送完成:")
        self.stdout.write(f"  成功: {success_count}")
        self.stdout.write(f"  失败: {failure_count}")
        self.stdout.write(f"  总计: {success_count + failure_count}")
        
        if success_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"成功发送了 {success_count} 封邮件")
            )
        
        if failure_count > 0:
            self.stdout.write(
                self.style.ERROR(f"有 {failure_count} 封邮件发送失败")
            )
