from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.crypto import get_random_string
from .forms import UserRegistrationForm, UserLoginForm
from .models import User, EmailVerification


def register_view(request):
    """用户注册视图"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # 需要邮箱验证后才能激活
            user.save()

            # 创建邮箱验证记录
            token = get_random_string(32)
            EmailVerification.objects.create(user=user, token=token)

            # 发送验证邮件
            verification_url = request.build_absolute_uri(
                reverse('accounts:verify_email', kwargs={'token': token})
            )

            try:
                send_mail(
                    subject='天气订阅系统 - 邮箱验证',
                    message=f'请点击以下链接验证您的邮箱：\n{verification_url}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                messages.success(request, '注册成功！请检查您的邮箱并点击验证链接。')
                return redirect('accounts:login')
            except Exception as e:
                messages.error(request, f'邮件发送失败：{str(e)}')
                user.delete()  # 删除用户记录
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """用户登录视图"""
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, '账户未激活，请先验证邮箱。')
            else:
                login(request, user)
                messages.success(request, '登录成功！')
                return redirect('weather:dashboard')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """用户登出视图"""
    logout(request)
    messages.success(request, '已成功登出。')
    return redirect('accounts:login')


def verify_email(request, token):
    """邮箱验证视图"""
    try:
        verification = EmailVerification.objects.get(token=token, is_used=False)
        user = verification.user
        user.is_active = True
        user.is_email_verified = True
        user.save()

        verification.is_used = True
        verification.save()

        messages.success(request, '邮箱验证成功！您现在可以登录了。')
        return redirect('accounts:login')
    except EmailVerification.DoesNotExist:
        messages.error(request, '验证链接无效或已过期。')
        return redirect('accounts:register')


@login_required
def profile_view(request):
    """用户个人资料视图"""
    return render(request, 'accounts/profile.html', {'user': request.user})
