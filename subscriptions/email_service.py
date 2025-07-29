from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from weather.services import WeatherService
from .models import EmailLog
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """邮件发送服务"""
    
    def __init__(self):
        self.weather_service = WeatherService()
    
    def send_weather_email(self, subscription):
        """
        发送天气邮件
        :param subscription: 订阅对象
        :return: 是否发送成功
        """
        try:
            # 获取天气数据
            weather_info = self.weather_service.get_weather_for_email(
                subscription.city.adcode
            )
            
            if not weather_info:
                logger.error(f"无法获取天气数据: {subscription.city.name}")
                self._log_email_error(
                    subscription, 
                    "天气数据获取失败", 
                    f"无法获取 {subscription.city.name} 的天气数据"
                )
                return False
            
            # 准备邮件内容
            context = {
                'city_name': weather_info['city_name'],
                'current': weather_info['current'],
                'forecast': weather_info['forecast'][:4],  # 只显示4天预报
                'current_date': timezone.now().strftime('%Y年%m月%d日'),
                'website_url': self._get_website_url(),
            }
            
            # 渲染邮件模板
            subject = f"☀️ {weather_info['city_name']} 今日天气预报"
            html_content = render_to_string('emails/weather_report.html', context)
            text_content = render_to_string('emails/weather_report.txt', context)
            
            # 创建邮件
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[subscription.email]
            )
            email.attach_alternative(html_content, "text/html")
            
            # 发送邮件
            email.send()
            
            # 记录发送成功
            self._log_email_success(subscription, subject, html_content)
            logger.info(f"天气邮件发送成功: {subscription.email} - {weather_info['city_name']}")
            
            return True

        except Exception as e:
            error_msg = str(e)
            logger.error(f"发送天气邮件失败: {subscription.email} - {error_msg}")
            self._log_email_error(subscription, "邮件发送失败", error_msg)
            return False

    def send_test_weather_email(self, subscription):
        """
        发送测试天气邮件
        :param subscription: 订阅对象
        :return: 是否发送成功
        """
        try:
            # 获取天气数据
            weather_info = self.weather_service.get_weather_for_email(
                subscription.city.adcode
            )

            if not weather_info:
                logger.error(f"无法获取天气数据: {subscription.city.name}")
                self._log_email_error(
                    subscription,
                    "测试邮件 - 天气数据获取失败",
                    f"无法获取 {subscription.city.name} 的天气数据"
                )
                return False

            # 准备邮件内容
            context = {
                'city_name': weather_info['city_name'],
                'current': weather_info['current'],
                'forecast': weather_info['forecast'][:4],  # 只显示4天预报
                'current_date': timezone.now().strftime('%Y年%m月%d日'),
                'website_url': self._get_website_url(),
                'is_test': True,  # 标记为测试邮件
            }

            # 渲染邮件模板
            subject = f"🧪 [测试邮件] {weather_info['city_name']} 天气预报"
            html_content = render_to_string('emails/weather_report.html', context)
            text_content = render_to_string('emails/weather_report.txt', context)

            # 创建邮件
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[subscription.email]
            )
            email.attach_alternative(html_content, "text/html")

            # 发送邮件
            email.send()

            # 记录发送成功
            self._log_email_success(subscription, subject, html_content)
            logger.info(f"测试天气邮件发送成功: {subscription.email} - {weather_info['city_name']}")

            return True

        except Exception as e:
            error_msg = str(e)
            logger.error(f"发送测试天气邮件失败: {subscription.email} - {error_msg}")
            self._log_email_error(subscription, "测试邮件发送失败", error_msg)
            return False

    def send_bulk_weather_emails(self, subscriptions):
        """
        批量发送天气邮件
        :param subscriptions: 订阅列表
        :return: (成功数量, 失败数量)
        """
        success_count = 0
        failure_count = 0
        
        for subscription in subscriptions:
            if self.send_weather_email(subscription):
                success_count += 1
            else:
                failure_count += 1
        
        logger.info(f"批量发送完成: 成功 {success_count}, 失败 {failure_count}")
        return success_count, failure_count
    
    def _log_email_success(self, subscription, subject, content):
        """记录邮件发送成功"""
        EmailLog.objects.create(
            subscription=subscription,
            email=subscription.email,
            subject=subject,
            content=content,
            is_sent=True
        )
    
    def _log_email_error(self, subscription, subject, error_message):
        """记录邮件发送失败"""
        EmailLog.objects.create(
            subscription=subscription,
            email=subscription.email,
            subject=subject,
            content="",
            is_sent=False,
            error_message=error_message
        )
    
    def _get_website_url(self):
        """获取网站URL"""
        # 在生产环境中应该从配置中获取
        return "http://localhost:8000"
    
    def test_email_sending(self, email_address, city_adcode="110101"):
        """
        测试邮件发送功能
        :param email_address: 测试邮箱
        :param city_adcode: 测试城市代码
        :return: 是否发送成功
        """
        try:
            # 获取天气数据
            weather_info = self.weather_service.get_weather_for_email(city_adcode)
            
            if not weather_info:
                logger.error("测试邮件: 无法获取天气数据")
                return False
            
            # 准备邮件内容
            context = {
                'city_name': weather_info['city_name'],
                'current': weather_info['current'],
                'forecast': weather_info['forecast'][:4],
                'current_date': timezone.now().strftime('%Y年%m月%d日'),
                'website_url': self._get_website_url(),
            }
            
            # 渲染邮件模板
            subject = f"🧪 测试邮件 - {weather_info['city_name']} 天气预报"
            html_content = render_to_string('emails/weather_report.html', context)
            text_content = render_to_string('emails/weather_report.txt', context)
            
            # 创建邮件
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email_address]
            )
            email.attach_alternative(html_content, "text/html")
            
            # 发送邮件
            email.send()
            
            logger.info(f"测试邮件发送成功: {email_address}")
            return True
            
        except Exception as e:
            logger.error(f"测试邮件发送失败: {email_address} - {str(e)}")
            return False
