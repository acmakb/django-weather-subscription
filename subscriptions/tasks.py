from celery import shared_task
from django.utils import timezone
from .models import Subscription
from .email_service import EmailService
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_daily_weather_emails():
    """
    每日定时发送天气邮件任务
    """
    logger.info("开始执行每日天气邮件发送任务")
    
    # 获取所有活跃的订阅
    active_subscriptions = Subscription.objects.filter(
        is_active=True
    ).select_related('user', 'city')
    
    if not active_subscriptions.exists():
        logger.info("没有活跃的订阅，任务结束")
        return "没有活跃的订阅"
    
    logger.info(f"找到 {active_subscriptions.count()} 个活跃订阅")
    
    # 创建邮件服务实例
    email_service = EmailService()
    
    # 批量发送邮件
    success_count, failure_count = email_service.send_bulk_weather_emails(
        active_subscriptions
    )
    
    result_message = f"邮件发送完成: 成功 {success_count}, 失败 {failure_count}"
    logger.info(result_message)
    
    return result_message


@shared_task
def send_weather_email_for_subscription(subscription_id):
    """
    为单个订阅发送天气邮件
    """
    try:
        subscription = Subscription.objects.get(
            id=subscription_id,
            is_active=True
        )

        email_service = EmailService()
        success = email_service.send_weather_email(subscription)

        if success:
            logger.info(f"订阅 {subscription_id} 邮件发送成功")
            return f"订阅 {subscription_id} 邮件发送成功"
        else:
            logger.error(f"订阅 {subscription_id} 邮件发送失败")
            return f"订阅 {subscription_id} 邮件发送失败"

    except Subscription.DoesNotExist:
        error_msg = f"订阅 {subscription_id} 不存在或已停用"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"订阅 {subscription_id} 邮件发送异常: {str(e)}"
        logger.error(error_msg)
        return error_msg


@shared_task
def send_weather_email(subscription_id, is_test=False):
    """
    发送天气邮件（支持测试模式）
    """
    try:
        subscription = Subscription.objects.get(
            id=subscription_id,
            is_active=True
        )

        email_service = EmailService()

        if is_test:
            # 测试模式：发送测试邮件
            success = email_service.send_test_weather_email(subscription)
            action = "测试邮件"
        else:
            # 正常模式：发送天气邮件
            success = email_service.send_weather_email(subscription)
            action = "天气邮件"

        if success:
            logger.info(f"订阅 {subscription_id} {action}发送成功")
            return f"订阅 {subscription_id} {action}发送成功"
        else:
            logger.error(f"订阅 {subscription_id} {action}发送失败")
            return f"订阅 {subscription_id} {action}发送失败"

    except Subscription.DoesNotExist:
        error_msg = f"订阅 {subscription_id} 不存在或已停用"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"订阅 {subscription_id} 邮件发送异常: {str(e)}"
        logger.error(error_msg)
        return error_msg


@shared_task
def test_celery_task():
    """
    测试Celery任务
    """
    current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"Celery任务测试成功！当前时间: {current_time}"
    logger.info(message)
    return message


@shared_task
def cleanup_old_email_logs():
    """
    清理旧的邮件日志（保留30天）
    """
    from datetime import timedelta
    from .models import EmailLog
    
    cutoff_date = timezone.now() - timedelta(days=30)
    
    deleted_count, _ = EmailLog.objects.filter(
        sent_at__lt=cutoff_date
    ).delete()
    
    message = f"清理了 {deleted_count} 条旧邮件日志"
    logger.info(message)
    return message
