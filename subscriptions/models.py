from django.db import models
from django.conf import settings
from weather.models import City


class Subscription(models.Model):
    """天气订阅模型"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name="订阅城市")
    email = models.EmailField(verbose_name="接收邮箱")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "天气订阅"
        verbose_name_plural = "天气订阅"
        unique_together = ['user', 'city']  # 用户对同一城市只能订阅一次
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.city.name}"


class EmailLog(models.Model):
    """邮件发送日志"""
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, verbose_name="订阅")
    email = models.EmailField(verbose_name="接收邮箱")
    subject = models.CharField(max_length=200, verbose_name="邮件主题")
    content = models.TextField(verbose_name="邮件内容")
    is_sent = models.BooleanField(default=False, verbose_name="是否发送成功")
    error_message = models.TextField(null=True, blank=True, verbose_name="错误信息")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="发送时间")

    class Meta:
        verbose_name = "邮件日志"
        verbose_name_plural = "邮件日志"
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.email} - {self.subject}"
