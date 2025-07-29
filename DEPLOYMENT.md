# 天气订阅系统 Linux 部署文档

## 📋 目录
- [系统要求](#系统要求)
- [环境准备](#环境准备)
- [数据库配置](#数据库配置)
- [Redis配置](#redis配置)
- [项目部署](#项目部署)
- [Nginx配置](#nginx配置)
- [Supervisor配置](#supervisor配置)
- [SSL证书配置](#ssl证书配置)
- [监控和日志](#监控和日志)
- [常见问题](#常见问题)

## 🖥️ 系统要求

### 操作系统
- Ubuntu 20.04 LTS 或更高版本
- CentOS 8 或更高版本
- Debian 11 或更高版本

### 硬件要求
- CPU: 2核心或以上
- 内存: 4GB RAM 或以上
- 存储: 20GB 可用空间或以上
- 网络: 稳定的互联网连接

## 🔧 环境准备

### 1. 更新系统包
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
# 或者 (CentOS 8+)
sudo dnf update -y
```

### 2. 安装基础依赖
```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y build-essential libssl-dev libffi-dev
sudo apt install -y git curl wget vim

# CentOS/RHEL
sudo yum install -y python3 python3-pip python3-devel
sudo yum install -y gcc gcc-c++ make openssl-devel libffi-devel
sudo yum install -y git curl wget vim
```

### 3. 创建项目用户
```bash
# 创建专用用户
sudo useradd -m -s /bin/bash weatherapp
sudo usermod -aG sudo weatherapp

# 切换到项目用户
sudo su - weatherapp
```

## 🗄️ 数据库配置

### 1. 安装MySQL
```bash
# Ubuntu/Debian
sudo apt install -y mysql-server mysql-client

# CentOS/RHEL
sudo yum install -y mysql-server
# 或者
sudo dnf install -y mysql-server
```

> **注意**: 由于使用PyMySQL替代mysqlclient，不再需要安装libmysqlclient-dev或mysql-devel开发库

### 2. 配置MySQL
```bash
# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 安全配置
sudo mysql_secure_installation
```

### 3. 创建数据库和用户
```sql
-- 登录MySQL
sudo mysql -u root -p

-- 创建数据库
CREATE DATABASE weatherblog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户并授权
CREATE USER 'weatherapp'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON weatherblog.* TO 'weatherapp'@'localhost';
FLUSH PRIVILEGES;

-- 退出
EXIT;
```

## 🔴 Redis配置

### 1. 安装Redis
```bash
# Ubuntu/Debian
sudo apt install -y redis-server

# CentOS/RHEL
sudo yum install -y redis
# 或者
sudo dnf install -y redis
```

### 2. 配置Redis
```bash
# 编辑配置文件
sudo vim /etc/redis/redis.conf

# 修改以下配置
bind 127.0.0.1
port 6379
requirepass your_redis_password
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### 3. 启动Redis
```bash
sudo systemctl start redis
sudo systemctl enable redis

# 测试连接
redis-cli ping
```

## 🚀 项目部署

### 1. 克隆项目
```bash
# 切换到项目用户
sudo su - weatherapp

# 创建项目目录
mkdir -p /home/weatherapp/projects
cd /home/weatherapp/projects

# 克隆项目 (假设您已经将项目上传到Git仓库)
git clone https://github.com/yourusername/weatherblog.git
cd weatherblog
```

### 2. 创建虚拟环境
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip
```

> **数据库驱动说明**: 本项目使用PyMySQL替代mysqlclient，避免了在Linux环境下编译mysqlclient时遇到的依赖问题。PyMySQL是纯Python实现的MySQL驱动，安装简单且兼容性好。

### 3. 安装依赖
```bash
# 安装Python依赖
pip install -r requirements.txt

# 如果安装mysqlclient出错，先安装系统依赖
# Ubuntu/Debian
sudo apt install -y pkg-config

# 然后重新安装
pip install mysqlclient
```

### 4. 配置环境变量
```bash
# 创建环境变量文件
vim .env
```

```bash
# .env 文件内容
DEBUG=False
SECRET_KEY=your_very_secure_secret_key_here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip

# 数据库配置
DB_NAME=weatherblog
DB_USER=weatherapp
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=3306

# Redis配置
REDIS_URL=redis://:your_redis_password@localhost:6379/0

# 邮件配置
EMAIL_HOST_USER=1480647675@qq.com
EMAIL_HOST_PASSWORD=qglblrluavuzijcg

# 天气API配置
WEATHER_API_KEY=d6a3b63a2d03bba441ed787070a7e308
```

### 5. 更新Django设置
```bash
# 编辑设置文件
vim weatherblog/settings.py
```

需要修改的配置：
```python
import os
from pathlib import Path

# 从环境变量读取配置
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# 数据库配置
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
        },
    }
}

# Redis配置
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = '/home/weatherapp/projects/weatherblog/staticfiles'

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/weatherapp/projects/weatherblog/media'

# 安全配置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/home/weatherapp/projects/weatherblog/logs/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### 6. 数据库迁移和初始化
```bash
# 激活虚拟环境
source venv/bin/activate

# 创建日志目录
mkdir -p logs

# 收集静态文件
python manage.py collectstatic --noinput

# 执行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 导入城市数据 (如果有城市数据文件)
python manage.py shell
```

```python
# 在Django shell中执行
from weather.models import City
import pandas as pd

# 读取城市数据文件
df = pd.read_excel('AMap_adcode_citycode.xlsx')
# 根据您的数据文件结构导入城市数据
# 这里需要根据实际的Excel文件结构来调整
```

## 🌐 Nginx配置

### 1. 安装Nginx
```bash
# Ubuntu/Debian
sudo apt install -y nginx

# CentOS/RHEL
sudo yum install -y nginx
# 或者
sudo dnf install -y nginx
```

### 2. 配置Nginx
```bash
# 创建站点配置文件
sudo vim /etc/nginx/sites-available/weatherblog
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL证书配置 (稍后配置)
    # ssl_certificate /path/to/your/certificate.crt;
    # ssl_certificate_key /path/to/your/private.key;

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";

    # 静态文件
    location /static/ {
        alias /home/weatherapp/projects/weatherblog/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 媒体文件
    location /media/ {
        alias /home/weatherapp/projects/weatherblog/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Django应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # 限制文件上传大小
    client_max_body_size 10M;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
```

### 3. 启用站点
```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/weatherblog /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## 🔧 Supervisor配置

### 1. 安装Supervisor
```bash
# Ubuntu/Debian
sudo apt install -y supervisor

# CentOS/RHEL
sudo yum install -y supervisor
# 或者
sudo dnf install -y supervisor
```

### 2. 安装Gunicorn
```bash
# 激活虚拟环境
source venv/bin/activate

# 安装Gunicorn
pip install gunicorn

# 创建Gunicorn配置文件
vim gunicorn.conf.py
```

```python
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
daemon = False
user = "weatherapp"
group = "weatherapp"
tmp_upload_dir = None
errorlog = "/home/weatherapp/projects/weatherblog/logs/gunicorn_error.log"
accesslog = "/home/weatherapp/projects/weatherblog/logs/gunicorn_access.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
```

### 3. 配置Django应用
```bash
# 创建Django应用配置
sudo vim /etc/supervisor/conf.d/weatherblog.conf
```

```ini
[program:weatherblog]
command=/home/weatherapp/projects/weatherblog/venv/bin/gunicorn -c gunicorn.conf.py weatherblog.wsgi:application
directory=/home/weatherapp/projects/weatherblog
user=weatherapp
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/weatherapp/projects/weatherblog/logs/gunicorn.log
environment=PATH="/home/weatherapp/projects/weatherblog/venv/bin"
```

### 4. 配置Celery Worker
```bash
# 创建Celery Worker配置
sudo vim /etc/supervisor/conf.d/celery.conf
```

```ini
[program:celery]
command=/home/weatherapp/projects/weatherblog/venv/bin/celery -A weatherblog worker -l info
directory=/home/weatherapp/projects/weatherblog
user=weatherapp
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/weatherapp/projects/weatherblog/logs/celery.log
environment=PATH="/home/weatherapp/projects/weatherblog/venv/bin"
```

### 5. 配置Celery Beat
```bash
# 创建Celery Beat配置
sudo vim /etc/supervisor/conf.d/celerybeat.conf
```

```ini
[program:celerybeat]
command=/home/weatherapp/projects/weatherblog/venv/bin/celery -A weatherblog beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=/home/weatherapp/projects/weatherblog
user=weatherapp
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/weatherapp/projects/weatherblog/logs/celerybeat.log
environment=PATH="/home/weatherapp/projects/weatherblog/venv/bin"
```

### 6. 启动服务
```bash
# 重新加载Supervisor配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动所有服务
sudo supervisorctl start weatherblog
sudo supervisorctl start celery
sudo supervisorctl start celerybeat

# 检查状态
sudo supervisorctl status
```

## 🔒 SSL证书配置

### 1. 使用Let's Encrypt (推荐)
```bash
# 安装Certbot
# Ubuntu/Debian
sudo apt install -y certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install -y certbot python3-certbot-nginx
# 或者
sudo dnf install -y certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 设置自动续期
sudo crontab -e
# 添加以下行
0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. 手动配置SSL证书
如果您有自己的SSL证书，请修改Nginx配置：
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL证书配置
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 其他配置...
}
```

## 📊 监控和日志

### 1. 日志文件位置
```bash
# Django应用日志
/home/weatherapp/projects/weatherblog/logs/django.log

# Gunicorn日志
/home/weatherapp/projects/weatherblog/logs/gunicorn.log
/home/weatherapp/projects/weatherblog/logs/gunicorn_error.log
/home/weatherapp/projects/weatherblog/logs/gunicorn_access.log

# Celery日志
/home/weatherapp/projects/weatherblog/logs/celery.log
/home/weatherapp/projects/weatherblog/logs/celerybeat.log

# Nginx日志
/var/log/nginx/access.log
/var/log/nginx/error.log

# 系统日志
/var/log/syslog
```

### 2. 日志轮转配置
```bash
# 创建日志轮转配置
sudo vim /etc/logrotate.d/weatherblog
```

```bash
/home/weatherapp/projects/weatherblog/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 weatherapp weatherapp
    postrotate
        sudo supervisorctl restart weatherblog
        sudo supervisorctl restart celery
        sudo supervisorctl restart celerybeat
    endscript
}
```

### 3. 系统监控脚本
```bash
# 创建监控脚本
vim /home/weatherapp/projects/weatherblog/monitor.sh
```

```bash
#!/bin/bash
# 系统监控脚本

LOG_FILE="/home/weatherapp/projects/weatherblog/logs/monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] 开始系统检查" >> $LOG_FILE

# 检查服务状态
services=("weatherblog" "celery" "celerybeat")
for service in "${services[@]}"; do
    status=$(sudo supervisorctl status $service | awk '{print $2}')
    if [ "$status" != "RUNNING" ]; then
        echo "[$DATE] 警告: $service 服务未运行" >> $LOG_FILE
        sudo supervisorctl start $service
    else
        echo "[$DATE] $service 服务正常运行" >> $LOG_FILE
    fi
done

# 检查磁盘空间
disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $disk_usage -gt 80 ]; then
    echo "[$DATE] 警告: 磁盘使用率超过80%: ${disk_usage}%" >> $LOG_FILE
fi

# 检查内存使用
memory_usage=$(free | awk 'NR==2{printf "%.2f", $3*100/$2}')
if (( $(echo "$memory_usage > 80" | bc -l) )); then
    echo "[$DATE] 警告: 内存使用率超过80%: ${memory_usage}%" >> $LOG_FILE
fi

echo "[$DATE] 系统检查完成" >> $LOG_FILE
```

```bash
# 设置执行权限
chmod +x /home/weatherapp/projects/weatherblog/monitor.sh

# 添加到定时任务
crontab -e
# 添加以下行 (每5分钟检查一次)
*/5 * * * * /home/weatherapp/projects/weatherblog/monitor.sh
```

## 🔧 常见问题

### 1. 数据库连接问题
```bash
# 检查MySQL服务状态
sudo systemctl status mysql

# 检查数据库连接
mysql -u weatherapp -p weatherblog

# 检查防火墙设置
sudo ufw status
```

### 2. Redis连接问题
```bash
# 检查Redis服务状态
sudo systemctl status redis

# 测试Redis连接
redis-cli ping

# 检查Redis配置
sudo vim /etc/redis/redis.conf
```

### 3. 静态文件问题
```bash
# 重新收集静态文件
source venv/bin/activate
python manage.py collectstatic --noinput

# 检查文件权限
sudo chown -R weatherapp:weatherapp /home/weatherapp/projects/weatherblog/
sudo chmod -R 755 /home/weatherapp/projects/weatherblog/staticfiles/
```

### 4. Celery任务问题
```bash
# 检查Celery状态
sudo supervisorctl status celery
sudo supervisorctl status celerybeat

# 重启Celery服务
sudo supervisorctl restart celery
sudo supervisorctl restart celerybeat

# 查看Celery日志
tail -f /home/weatherapp/projects/weatherblog/logs/celery.log
```

### 5. 邮件发送问题
```bash
# 测试邮件配置
python manage.py shell
```

```python
from django.core.mail import send_mail
send_mail(
    '测试邮件',
    '这是一封测试邮件',
    '1480647675@qq.com',
    ['test@example.com'],
    fail_silently=False,
)
```

### 6. 性能优化建议
```bash
# 1. 数据库优化
# 在MySQL中添加索引
ALTER TABLE subscriptions_subscription ADD INDEX idx_user_city (user_id, city_id);
ALTER TABLE subscriptions_emaillog ADD INDEX idx_created_at (created_at);

# 2. Redis内存优化
# 在redis.conf中设置
maxmemory 512mb
maxmemory-policy allkeys-lru

# 3. Nginx缓存优化
# 在Nginx配置中添加
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 🚀 部署完成检查清单

- [ ] 系统环境准备完成
- [ ] MySQL数据库安装并配置
- [ ] Redis服务安装并配置
- [ ] Python虚拟环境创建
- [ ] 项目依赖安装完成
- [ ] 数据库迁移执行
- [ ] 超级用户创建
- [ ] 静态文件收集
- [ ] Nginx配置并启动
- [ ] Supervisor配置并启动
- [ ] SSL证书配置 (可选)
- [ ] 日志轮转配置
- [ ] 监控脚本配置
- [ ] 防火墙配置
- [ ] 定时任务测试
- [ ] 邮件发送测试
- [ ] 网站访问测试

## 📞 技术支持

如果在部署过程中遇到问题，请检查：
1. 系统日志: `sudo journalctl -f`
2. 应用日志: `tail -f /home/weatherapp/projects/weatherblog/logs/*.log`
3. Nginx日志: `sudo tail -f /var/log/nginx/error.log`
4. 服务状态: `sudo supervisorctl status`

祝您部署顺利！🎉
