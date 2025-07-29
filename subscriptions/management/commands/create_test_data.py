from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from weather.models import City
from subscriptions.models import Subscription

User = get_user_model()


class Command(BaseCommand):
    help = '创建测试数据'

    def handle(self, *args, **options):
        self.stdout.write("正在创建测试数据...")
        
        # 创建测试用户
        test_user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'username': 'testuser',
                'is_active': True,
                'is_email_verified': True
            }
        )
        
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write("创建了测试用户: test@example.com / testpass123")
        else:
            self.stdout.write("测试用户已存在")
        
        # 创建测试订阅
        try:
            # 北京东城区
            beijing_city = City.objects.get(adcode='110101')
            subscription1, created = Subscription.objects.get_or_create(
                user=test_user,
                city=beijing_city,
                defaults={
                    'email': '1480647675@qq.com',
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f"创建了订阅: {beijing_city.get_full_name()}")
            else:
                self.stdout.write(f"订阅已存在: {beijing_city.get_full_name()}")
            
            # 上海黄浦区
            shanghai_city = City.objects.get(adcode='310101')
            subscription2, created = Subscription.objects.get_or_create(
                user=test_user,
                city=shanghai_city,
                defaults={
                    'email': '1480647675@qq.com',
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f"创建了订阅: {shanghai_city.get_full_name()}")
            else:
                self.stdout.write(f"订阅已存在: {shanghai_city.get_full_name()}")
                
        except City.DoesNotExist as e:
            self.stdout.write(
                self.style.ERROR(f"城市不存在: {str(e)}")
            )
        
        self.stdout.write(
            self.style.SUCCESS("测试数据创建完成！")
        )
        self.stdout.write("测试用户登录信息:")
        self.stdout.write("邮箱: test@example.com")
        self.stdout.write("密码: testpass123")
