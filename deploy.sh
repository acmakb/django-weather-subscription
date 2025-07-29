#!/bin/bash

# 天气订阅系统部署脚本
# 使用方法: chmod +x deploy.sh && ./deploy.sh

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用root用户运行此脚本"
        exit 1
    fi
}

# 检查操作系统
check_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
        log_info "检测到操作系统: $OS $VER"
    else
        log_error "无法检测操作系统"
        exit 1
    fi
}

# 安装系统依赖
install_system_deps() {
    log_info "安装系统依赖..."
    
    if [[ $OS == *"Ubuntu"* ]] || [[ $OS == *"Debian"* ]]; then
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv python3-dev
        sudo apt install -y build-essential libssl-dev libffi-dev
        sudo apt install -y mysql-server mysql-client
        sudo apt install -y redis-server
        sudo apt install -y nginx supervisor
        sudo apt install -y git curl wget vim pkg-config
    elif [[ $OS == *"CentOS"* ]] || [[ $OS == *"Red Hat"* ]]; then
        sudo yum update -y
        sudo yum install -y python3 python3-pip python3-devel
        sudo yum install -y gcc gcc-c++ make openssl-devel libffi-devel
        sudo yum install -y mysql-server
        sudo yum install -y redis
        sudo yum install -y nginx supervisor
        sudo yum install -y git curl wget vim
    else
        log_error "不支持的操作系统: $OS"
        exit 1
    fi
    
    log_success "系统依赖安装完成"
}

# 配置MySQL
setup_mysql() {
    log_info "配置MySQL..."
    
    # 启动MySQL服务
    sudo systemctl start mysql
    sudo systemctl enable mysql
    
    # 检查MySQL是否运行
    if ! sudo systemctl is-active --quiet mysql; then
        log_error "MySQL服务启动失败"
        exit 1
    fi
    
    log_success "MySQL配置完成"
}

# 配置Redis
setup_redis() {
    log_info "配置Redis..."
    
    # 启动Redis服务
    sudo systemctl start redis
    sudo systemctl enable redis
    
    # 检查Redis是否运行
    if ! sudo systemctl is-active --quiet redis; then
        log_error "Redis服务启动失败"
        exit 1
    fi
    
    log_success "Redis配置完成"
}

# 创建虚拟环境
setup_venv() {
    log_info "创建Python虚拟环境..."
    
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
        log_success "虚拟环境创建完成"
    else
        log_warning "虚拟环境已存在"
    fi
    
    # 激活虚拟环境并安装依赖
    source venv/bin/activate
    pip install --upgrade pip
    
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        log_success "Python依赖安装完成"
    else
        log_error "requirements.txt文件不存在"
        exit 1
    fi
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    mkdir -p logs
    mkdir -p staticfiles
    mkdir -p media
    
    log_success "目录创建完成"
}

# 配置环境变量
setup_env() {
    log_info "配置环境变量..."
    
    if [[ ! -f ".env" ]]; then
        cat > .env << EOF
DEBUG=False
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置
DB_NAME=weatherblog
DB_USER=weatherapp
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=3306

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 邮件配置
EMAIL_HOST_USER=1480647675@qq.com
EMAIL_HOST_PASSWORD=qglblrluavuzijcg

# 天气API配置
WEATHER_API_KEY=d6a3b63a2d03bba441ed787070a7e308
EOF
        log_success "环境变量文件创建完成"
        log_warning "请编辑 .env 文件，设置正确的配置参数"
    else
        log_warning ".env 文件已存在"
    fi
}

# 数据库迁移
migrate_database() {
    log_info "执行数据库迁移..."
    
    source venv/bin/activate
    
    # 收集静态文件
    python manage.py collectstatic --noinput
    
    # 执行迁移
    python manage.py makemigrations
    python manage.py migrate
    
    log_success "数据库迁移完成"
}

# 配置Nginx
setup_nginx() {
    log_info "配置Nginx..."
    
    # 获取当前用户和项目路径
    CURRENT_USER=$(whoami)
    PROJECT_PATH=$(pwd)
    
    # 创建Nginx配置文件
    sudo tee /etc/nginx/sites-available/weatherblog > /dev/null << EOF
server {
    listen 80;
    server_name _;
    
    # 静态文件
    location /static/ {
        alias $PROJECT_PATH/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 媒体文件
    location /media/ {
        alias $PROJECT_PATH/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Django应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
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
EOF
    
    # 启用站点
    sudo ln -sf /etc/nginx/sites-available/weatherblog /etc/nginx/sites-enabled/
    
    # 测试配置
    sudo nginx -t
    
    # 重启Nginx
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    
    log_success "Nginx配置完成"
}

# 配置Supervisor
setup_supervisor() {
    log_info "配置Supervisor..."
    
    CURRENT_USER=$(whoami)
    PROJECT_PATH=$(pwd)
    
    # 安装Gunicorn
    source venv/bin/activate
    pip install gunicorn
    
    # 创建Gunicorn配置
    cat > gunicorn.conf.py << EOF
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
user = "$CURRENT_USER"
group = "$CURRENT_USER"
errorlog = "$PROJECT_PATH/logs/gunicorn_error.log"
accesslog = "$PROJECT_PATH/logs/gunicorn_access.log"
EOF
    
    # 创建Supervisor配置文件
    sudo tee /etc/supervisor/conf.d/weatherblog.conf > /dev/null << EOF
[program:weatherblog]
command=$PROJECT_PATH/venv/bin/gunicorn -c gunicorn.conf.py weatherblog.wsgi:application
directory=$PROJECT_PATH
user=$CURRENT_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$PROJECT_PATH/logs/gunicorn.log
environment=PATH="$PROJECT_PATH/venv/bin"
EOF
    
    sudo tee /etc/supervisor/conf.d/celery.conf > /dev/null << EOF
[program:celery]
command=$PROJECT_PATH/venv/bin/celery -A weatherblog worker -l info
directory=$PROJECT_PATH
user=$CURRENT_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$PROJECT_PATH/logs/celery.log
environment=PATH="$PROJECT_PATH/venv/bin"
EOF
    
    sudo tee /etc/supervisor/conf.d/celerybeat.conf > /dev/null << EOF
[program:celerybeat]
command=$PROJECT_PATH/venv/bin/celery -A weatherblog beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=$PROJECT_PATH
user=$CURRENT_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$PROJECT_PATH/logs/celerybeat.log
environment=PATH="$PROJECT_PATH/venv/bin"
EOF
    
    # 重新加载Supervisor配置
    sudo supervisorctl reread
    sudo supervisorctl update
    
    # 启动服务
    sudo supervisorctl start weatherblog
    sudo supervisorctl start celery
    sudo supervisorctl start celerybeat
    
    log_success "Supervisor配置完成"
}

# 主函数
main() {
    log_info "开始部署天气订阅系统..."
    
    check_root
    check_os
    install_system_deps
    setup_mysql
    setup_redis
    setup_venv
    create_directories
    setup_env
    migrate_database
    setup_nginx
    setup_supervisor
    
    log_success "部署完成！"
    log_info "请访问 http://your-server-ip 查看网站"
    log_info "管理后台地址: http://your-server-ip/admin/"
    log_warning "请记得："
    log_warning "1. 编辑 .env 文件设置正确的配置"
    log_warning "2. 创建MySQL数据库和用户"
    log_warning "3. 创建Django超级用户: python manage.py createsuperuser"
    log_warning "4. 配置防火墙和SSL证书"
}

# 运行主函数
main "$@"
