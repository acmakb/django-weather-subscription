"""
URL configuration for weatherblog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from subscriptions.admin_views import admin_dashboard, user_statistics
from subscriptions.admin import toggle_subscription
from .admin import CustomAuthenticationForm

# 设置默认admin站点的登录表单
admin.site.login_form = CustomAuthenticationForm
admin.site.site_header = '天气订阅系统管理后台'
admin.site.site_title = '天气订阅系统'
admin.site.index_title = '欢迎使用天气订阅系统管理后台'

urlpatterns = [
    path("admin/dashboard/", admin_dashboard, name="admin_dashboard"),
    path("admin/user-statistics/", user_statistics, name="admin_user_statistics"),
    path("admin/toggle-subscription/<int:subscription_id>/", toggle_subscription, name="toggle_subscription"),
    path("admin/", admin.site.urls),
    path("", include("weather.urls")),
    path("accounts/", include("accounts.urls")),
    path("subscriptions/", include("subscriptions.urls")),
]

# 开发环境下提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
