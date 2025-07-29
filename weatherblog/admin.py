from django.contrib import admin
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.core.exceptions import ValidationError


class CustomAuthenticationForm(AuthenticationForm):
    """自定义登录表单 - 使用邮箱登录"""

    username = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(attrs={
            'placeholder': '请输入邮箱地址',
            'class': 'form-control',
            'autofocus': True
        })
    )

    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={
            'placeholder': '请输入密码',
            'class': 'form-control'
        })
    )

    error_messages = {
        'invalid_login': '请输入一个正确的邮箱和密码。注意，两者都区分大小写。',
        'inactive': '此账户已被禁用。',
    }


class CustomAdminSite(admin.AdminSite):
    """自定义Admin站点"""
    site_header = '天气订阅系统管理后台'
    site_title = '天气订阅系统'
    index_title = '欢迎使用天气订阅系统管理后台'
    login_form = CustomAuthenticationForm
    
    def login(self, request, extra_context=None):
        """自定义登录视图"""
        if extra_context is None:
            extra_context = {}
        extra_context.update({
            'title': '登录',
            'subtitle': '请使用邮箱和密码登录',
        })
        return super().login(request, extra_context)


# 创建自定义admin站点实例
admin_site = CustomAdminSite(name='custom_admin')
