"""
生产环境配置文件
使用方法: python manage.py runserver --settings=weatherblog.settings_production
或设置环境变量: export DJANGO_SETTINGS_MODULE=weatherblog.settings_production
"""

import os
from pathlib import Path

# 配置PyMySQL作为MySQLdb的替代
import pymysql
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 从环境变量读取配置
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'your-very-secure-secret-key-here')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Application definition
INSTALLED_APPS = [
    "simpleui",  # SimpleUI必须放在django.contrib.admin之前
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_beat",
    "accounts",
    "weather",
    "subscriptions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "weatherblog.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "weatherblog.wsgi.application"

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'weatherblog'),
        'USER': os.getenv('DB_USER', 'weatherapp'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'your qq@qq.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'your auth password')
DEFAULT_FROM_EMAIL = os.getenv('EMAIL_HOST_USER', 'your qq@qq.com')

# Celery settings
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Weather API settings
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', 'you key')
WEATHER_API_URL = 'https://restapi.amap.com/v3/weather/weatherInfo'

# 安全配置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTPS配置 (如果使用HTTPS)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django_error.log'),
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'weatherblog': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# SimpleUI配置
SIMPLEUI_CONFIG = {
    'system_keep': False,
    'menu_display': ['用户管理', '天气管理', '订阅管理', '系统管理'],
    'dynamic': True,
    'menus': [
        {
            'name': '系统概览',
            'icon': 'fas fa-tachometer-alt',
            'url': '/admin/dashboard/',
        },
        {
            'app': 'accounts',
            'name': '用户管理',
            'icon': 'fas fa-users',
            'models': [
                {
                    'name': '用户',
                    'icon': 'fas fa-user',
                    'url': '/admin/accounts/user/'
                },
                {
                    'name': '邮箱验证',
                    'icon': 'fas fa-envelope-open',
                    'url': '/admin/accounts/emailverification/'
                }
            ]
        },
        {
            'app': 'weather',
            'name': '天气管理',
            'icon': 'fas fa-cloud-sun',
            'models': [
                {
                    'name': '城市',
                    'icon': 'fas fa-city',
                    'url': '/admin/weather/city/'
                }
            ]
        },
        {
            'app': 'subscriptions',
            'name': '订阅管理',
            'icon': 'fas fa-bell',
            'models': [
                {
                    'name': '订阅',
                    'icon': 'fas fa-rss',
                    'url': '/admin/subscriptions/subscription/'
                },
                {
                    'name': '邮件日志',
                    'icon': 'fas fa-envelope',
                    'url': '/admin/subscriptions/emaillog/'
                }
            ]
        },
        {
            'name': '定时任务',
            'icon': 'fas fa-clock',
            'models': [
                {
                    'name': '周期任务',
                    'icon': 'fas fa-calendar-alt',
                    'url': '/admin/django_celery_beat/periodictask/'
                },
                {
                    'name': '定时计划',
                    'icon': 'fas fa-stopwatch',
                    'url': '/admin/django_celery_beat/crontabschedule/'
                }
            ]
        }
    ]
}
