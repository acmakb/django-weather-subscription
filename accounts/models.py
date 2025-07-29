from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """扩展用户模型"""
    email = models.EmailField(unique=True, verbose_name="邮箱")
    is_email_verified = models.BooleanField(default=False, verbose_name="邮箱已验证")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self):
        return self.email


class EmailVerification(models.Model):
    """邮箱验证模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    token = models.CharField(max_length=100, unique=True, verbose_name="验证令牌")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_used = models.BooleanField(default=False, verbose_name="已使用")

    class Meta:
        verbose_name = "邮箱验证"
        verbose_name_plural = "邮箱验证"

    def __str__(self):
        return f"{self.user.email} - {self.token}"
