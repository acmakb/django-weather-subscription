from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, EmailVerification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理"""
    list_display = ('email', 'username', 'is_email_verified', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_email_verified', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('额外信息', {'fields': ('is_email_verified',)}),
    )

    readonly_fields = ('date_joined', 'last_login')


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    """邮箱验证管理"""
    list_display = ('user', 'token', 'is_used', 'created_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'user__username', 'token')
    readonly_fields = ('token', 'created_at')
    ordering = ('-created_at',)
