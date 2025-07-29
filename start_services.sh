#!/bin/bash

# 天气订阅系统启动脚本
# 使用方法: chmod +x start_services.sh && ./start_services.sh

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

# 检查Redis服务
check_redis() {
    log_info "检查Redis服务..."
    
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping &> /dev/null; then
            log_success "Redis服务运行正常"
            return 0
        else
            log_error "Redis服务未运行，请启动Redis"
            log_info "启动命令: sudo systemctl start redis"
            return 1
        fi
    else
        log_error "Redis未安装，请先安装Redis"
        log_info "安装命令: sudo apt install redis-server"
        return 1
    fi
}

# 检查Python虚拟环境
check_venv() {
    log_info "检查Python虚拟环境..."
    
    if [[ -d "venv" ]]; then
        log_success "虚拟环境存在"
        return 0
    else
        log_error "虚拟环境不存在，请先创建"
        log_info "创建命令: python3 -m venv venv"
        return 1
    fi
}

# 检查依赖包
check_dependencies() {
    log_info "检查依赖包..."
    
    source venv/bin/activate
    
    # 检查关键包
    if python -c "import django, celery, redis" &> /dev/null; then
        log_success "关键依赖包已安装"
        return 0
    else
        log_error "依赖包缺失，请安装"
        log_info "安装命令: pip install -r requirements.txt"
        return 1
    fi
}

# 停止现有进程
stop_services() {
    log_info "停止现有服务..."
    
    # 停止Django
    pkill -f "python.*manage.py.*runserver" && log_info "已停止Django服务"
    
    # 停止Celery Worker
    pkill -f "celery.*worker" && log_info "已停止Celery Worker"
    
    # 停止Celery Beat
    pkill -f "celery.*beat" && log_info "已停止Celery Beat"
    
    sleep 2
}

# 启动Django服务
start_django() {
    log_info "启动Django服务..."
    
    source venv/bin/activate
    
    # 检查数据库连接
    if python manage.py check --database default &> /dev/null; then
        log_success "数据库连接正常"
    else
        log_error "数据库连接失败，请检查配置"
        return 1
    fi
    
    # 启动Django
    nohup python manage.py runserver 0.0.0.0:8001 > logs/django.log 2>&1 &
    DJANGO_PID=$!
    
    sleep 3
    
    if ps -p $DJANGO_PID > /dev/null; then
        log_success "Django服务启动成功 (PID: $DJANGO_PID)"
        echo $DJANGO_PID > logs/django.pid
        return 0
    else
        log_error "Django服务启动失败"
        return 1
    fi
}

# 启动Celery Worker
start_celery_worker() {
    log_info "启动Celery Worker..."
    
    source venv/bin/activate
    
    nohup celery -A weatherblog worker -l info > logs/celery_worker.log 2>&1 &
    WORKER_PID=$!
    
    sleep 3
    
    if ps -p $WORKER_PID > /dev/null; then
        log_success "Celery Worker启动成功 (PID: $WORKER_PID)"
        echo $WORKER_PID > logs/celery_worker.pid
        return 0
    else
        log_error "Celery Worker启动失败"
        return 1
    fi
}

# 启动Celery Beat
start_celery_beat() {
    log_info "启动Celery Beat..."
    
    source venv/bin/activate
    
    nohup celery -A weatherblog beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler > logs/celery_beat.log 2>&1 &
    BEAT_PID=$!
    
    sleep 3
    
    if ps -p $BEAT_PID > /dev/null; then
        log_success "Celery Beat启动成功 (PID: $BEAT_PID)"
        echo $BEAT_PID > logs/celery_beat.pid
        return 0
    else
        log_error "Celery Beat启动失败"
        return 1
    fi
}

# 设置定时任务
setup_periodic_tasks() {
    log_info "设置定时任务..."
    
    source venv/bin/activate
    
    if python manage.py setup_periodic_tasks &> /dev/null; then
        log_success "定时任务设置完成"
        return 0
    else
        log_warning "定时任务设置可能失败，请手动检查"
        return 1
    fi
}

# 显示服务状态
show_status() {
    log_info "服务状态检查..."
    
    echo "==================== 服务状态 ===================="
    
    # Django状态
    if [[ -f "logs/django.pid" ]] && ps -p $(cat logs/django.pid) > /dev/null 2>&1; then
        echo -e "Django:      ${GREEN}运行中${NC} (PID: $(cat logs/django.pid))"
    else
        echo -e "Django:      ${RED}未运行${NC}"
    fi
    
    # Celery Worker状态
    if [[ -f "logs/celery_worker.pid" ]] && ps -p $(cat logs/celery_worker.pid) > /dev/null 2>&1; then
        echo -e "Celery Worker: ${GREEN}运行中${NC} (PID: $(cat logs/celery_worker.pid))"
    else
        echo -e "Celery Worker: ${RED}未运行${NC}"
    fi
    
    # Celery Beat状态
    if [[ -f "logs/celery_beat.pid" ]] && ps -p $(cat logs/celery_beat.pid) > /dev/null 2>&1; then
        echo -e "Celery Beat:   ${GREEN}运行中${NC} (PID: $(cat logs/celery_beat.pid))"
    else
        echo -e "Celery Beat:   ${RED}未运行${NC}"
    fi
    
    # Redis状态
    if redis-cli ping &> /dev/null; then
        echo -e "Redis:       ${GREEN}运行中${NC}"
    else
        echo -e "Redis:       ${RED}未运行${NC}"
    fi
    
    echo "=================================================="
    echo ""
    echo "📱 访问地址:"
    echo "   网站首页: http://$(hostname -I | awk '{print $1}'):8001/"
    echo "   管理后台: http://$(hostname -I | awk '{print $1}'):8001/admin/"
    echo ""
    echo "📝 日志文件:"
    echo "   Django:      tail -f logs/django.log"
    echo "   Celery Worker: tail -f logs/celery_worker.log"
    echo "   Celery Beat:   tail -f logs/celery_beat.log"
    echo ""
    echo "🛑 停止服务: ./stop_services.sh"
}

# 主函数
main() {
    echo "=========================================="
    echo "🌤️  天气订阅系统启动脚本"
    echo "=========================================="
    
    # 创建日志目录
    mkdir -p logs
    
    # 检查环境
    if ! check_redis; then
        exit 1
    fi
    
    if ! check_venv; then
        exit 1
    fi
    
    if ! check_dependencies; then
        exit 1
    fi
    
    # 停止现有服务
    stop_services
    
    # 启动服务
    if start_django && start_celery_worker && start_celery_beat; then
        setup_periodic_tasks
        log_success "所有服务启动完成！"
        echo ""
        show_status
    else
        log_error "部分服务启动失败，请检查日志"
        exit 1
    fi
}

# 运行主函数
main "$@"
