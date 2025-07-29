from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Subscription, EmailLog


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """订阅管理"""
    list_display = ('user_info', 'city_info', 'email', 'is_active', 'created_at', 'action_buttons')
    list_filter = ('is_active', 'created_at', 'city__level')
    search_fields = ('user__email', 'user__username', 'city__name', 'email')
    ordering = ('-created_at',)
    list_per_page = 50
    actions = ['activate_subscriptions', 'deactivate_subscriptions', 'send_test_emails']
    actions = ['activate_subscriptions', 'deactivate_subscriptions']

    fieldsets = (
        ('订阅信息', {
            'fields': ('user', 'city', 'email', 'is_active')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def user_info(self, obj):
        """用户信息"""
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.user.username,
            obj.user.email
        )
    user_info.short_description = '用户'

    def city_info(self, obj):
        """城市信息"""
        return format_html(
            '<strong>{}</strong><br><small>代码: {}</small>',
            obj.city.get_full_name(),
            obj.city.adcode
        )
    city_info.short_description = '城市'

    def action_buttons(self, obj):
        """操作按钮"""
        toggle_text = '停用' if obj.is_active else '激活'
        toggle_color = 'red' if obj.is_active else 'green'
        toggle_url = reverse('toggle_subscription', args=[obj.id])

        return format_html(
            '<a href="{}" onclick="return toggleSubscription(this, {})" style="color: {}; text-decoration: none; padding: 5px 10px; border: 1px solid {}; border-radius: 3px;">{}</a>',
            toggle_url,
            obj.id,
            toggle_color,
            toggle_color,
            toggle_text
        )
    action_buttons.short_description = '操作'

    class Media:
        js = ('admin/js/subscription_toggle.js',)

    def activate_subscriptions(self, request, queryset):
        """批量激活订阅"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'成功激活了 {updated} 个订阅。',
            level='SUCCESS'
        )
    activate_subscriptions.short_description = "激活选中的订阅"

    def deactivate_subscriptions(self, request, queryset):
        """批量停用订阅"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'成功停用了 {updated} 个订阅。',
            level='SUCCESS'
        )
    deactivate_subscriptions.short_description = "停用选中的订阅"

    def send_test_emails(self, request, queryset):
        """批量发送测试邮件"""
        from .tasks import send_weather_email
        from django.utils import timezone

        # 只处理活跃的订阅
        active_subscriptions = queryset.filter(is_active=True)
        total_selected = queryset.count()
        active_count = active_subscriptions.count()

        if active_count == 0:
            self.message_user(
                request,
                f'选中的 {total_selected} 个订阅中没有活跃的订阅。',
                level='WARNING'
            )
            return

        success_count = 0
        error_count = 0

        for subscription in active_subscriptions:
            try:
                # 异步发送测试邮件
                send_weather_email.delay(subscription.id, is_test=True)
                success_count += 1
            except Exception:
                error_count += 1

        # 构建消息
        messages = []
        if success_count > 0:
            messages.append(f'成功为 {success_count} 个活跃订阅发送了测试邮件任务')

        if error_count > 0:
            messages.append(f'有 {error_count} 个订阅发送失败')

        if total_selected > active_count:
            messages.append(f'跳过了 {total_selected - active_count} 个非活跃订阅')

        # 显示结果消息
        if success_count > 0:
            self.message_user(request, '。'.join(messages) + '。', level='SUCCESS')
        else:
            self.message_user(request, '。'.join(messages) + '。', level='WARNING')

    send_test_emails.short_description = "为选中的活跃订阅发送测试邮件"


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """邮件日志管理"""
    list_display = ('subscription_info', 'email', 'subject', 'is_sent', 'sent_at', 'status')
    list_filter = ('is_sent', 'sent_at')
    search_fields = ('email', 'subject', 'subscription__user__username')
    ordering = ('-sent_at',)
    list_per_page = 50

    fieldsets = (
        ('邮件信息', {
            'fields': ('subscription', 'email', 'subject', 'is_sent')
        }),
        ('内容', {
            'fields': ('content',),
            'classes': ('collapse',)
        }),
        ('错误信息', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('sent_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('sent_at',)

    def subscription_info(self, obj):
        """订阅信息"""
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.subscription.user.username,
            obj.subscription.city.get_full_name()
        )
    subscription_info.short_description = '订阅'

    def status(self, obj):
        """发送状态"""
        if obj.is_sent:
            return format_html(
                '<span style="color: green;">✓ 成功</span>'
            )
        else:
            return format_html(
                '<span style="color: red;">✗ 失败</span>'
            )
    status.short_description = '状态'


# 自定义Admin站点标题
admin.site.site_header = '天气订阅系统管理后台'
admin.site.site_title = '天气订阅系统'
admin.site.index_title = '欢迎使用天气订阅系统管理后台'


# 订阅切换视图
@staff_member_required
@require_POST
@csrf_exempt
def toggle_subscription(request, subscription_id):
    """切换订阅状态"""
    try:
        subscription = get_object_or_404(Subscription, id=subscription_id)
        subscription.is_active = not subscription.is_active
        subscription.save()

        status_text = '激活' if subscription.is_active else '停用'
        return JsonResponse({
            'success': True,
            'is_active': subscription.is_active,
            'status_text': status_text,
            'message': f'订阅已{status_text}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'操作失败: {str(e)}'
        })
