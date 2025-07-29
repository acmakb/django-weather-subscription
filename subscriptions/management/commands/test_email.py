from django.core.management.base import BaseCommand
from subscriptions.email_service import EmailService


class Command(BaseCommand):
    help = '测试邮件发送功能'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='1480647675@qq.com',
            help='测试邮箱地址'
        )
        parser.add_argument(
            '--city',
            type=str,
            default='110101',  # 北京东城区
            help='城市adcode'
        )

    def handle(self, *args, **options):
        email_address = options['email']
        city_adcode = options['city']
        
        self.stdout.write(f"正在向 {email_address} 发送测试邮件...")
        
        email_service = EmailService()
        
        if email_service.test_email_sending(email_address, city_adcode):
            self.stdout.write(
                self.style.SUCCESS(f'测试邮件发送成功！请检查邮箱 {email_address}')
            )
        else:
            self.stdout.write(
                self.style.ERROR('测试邮件发送失败！请检查邮件配置')
            )
