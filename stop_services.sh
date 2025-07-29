#!/bin/bash

# 天气订阅系统停止脚本
# 使用方法: chmod +x stop_services.sh && ./stop_services.sh

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

# 停止服务函数
stop_service() {
    local service_name=$1
    local pid_file=$2
    local process_pattern=$3
    
    log_info "停止 $service_name..."
    
    # 尝试通过PID文件停止
    if [[ -f "$pid_file" ]]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            kill $pid
            sleep 2
            if ps -p $pid > /dev/null 2>&1; then
                log_warning "$service_name 进程仍在运行，强制终止..."
                kill -9 $pid
            fi
            rm -f "$pid_file"
            log_success "$service_name 已停止"
        else
            log_warning "$service_name PID文件存在但进程不存在"
            rm -f "$pid_file"
        fi
    fi
    
    # 通过进程模式停止
    if [[ -n "$process_pattern" ]]; then
        local pids=$(pgrep -f "$process_pattern")
        if [[ -n "$pids" ]]; then
            log_info "发现 $service_name 进程: $pids"
            pkill -f "$process_pattern"
            sleep 2
            
            # 检查是否还有残留进程
            local remaining_pids=$(pgrep -f "$process_pattern")
            if [[ -n "$remaining_pids" ]]; then
                log_warning "强制终止 $service_name 残留进程: $remaining_pids"
                pkill -9 -f "$process_pattern"
            fi
            log_success "$service_name 进程已清理"
        fi
    fi
}

# 显示当前运行的进程
show_running_processes() {
    log_info "当前运行的相关进程:"
    echo "==================== 进程列表 ===================="
    
    # Django进程
    local django_pids=$(pgrep -f "python.*manage.py.*runserver")
    if [[ -n "$django_pids" ]]; then
        echo -e "${YELLOW}Django进程:${NC}"
        ps -p $django_pids -o pid,ppid,cmd --no-headers
    fi
    
    # Celery Worker进程
    local worker_pids=$(pgrep -f "celery.*worker")
    if [[ -n "$worker_pids" ]]; then
        echo -e "${YELLOW}Celery Worker进程:${NC}"
        ps -p $worker_pids -o pid,ppid,cmd --no-headers
    fi
    
    # Celery Beat进程
    local beat_pids=$(pgrep -f "celery.*beat")
    if [[ -n "$beat_pids" ]]; then
        echo -e "${YELLOW}Celery Beat进程:${NC}"
        ps -p $beat_pids -o pid,ppid,cmd --no-headers
    fi
    
    echo "=================================================="
}

# 清理日志文件
cleanup_logs() {
    log_info "清理旧的PID文件..."
    
    rm -f logs/django.pid
    rm -f logs/celery_worker.pid
    rm -f logs/celery_beat.pid
    
    log_success "PID文件清理完成"
}

# 显示最终状态
show_final_status() {
    log_info "最终状态检查..."
    
    local django_running=$(pgrep -f "python.*manage.py.*runserver" | wc -l)
    local worker_running=$(pgrep -f "celery.*worker" | wc -l)
    local beat_running=$(pgrep -f "celery.*beat" | wc -l)
    
    echo "==================== 最终状态 ===================="
    echo -e "Django进程:    ${django_running} 个"
    echo -e "Celery Worker: ${worker_running} 个"
    echo -e "Celery Beat:   ${beat_running} 个"
    echo "=================================================="
    
    if [[ $django_running -eq 0 && $worker_running -eq 0 && $beat_running -eq 0 ]]; then
        log_success "所有服务已成功停止"
        return 0
    else
        log_warning "仍有进程在运行，可能需要手动清理"
        return 1
    fi
}

# 主函数
main() {
    echo "=========================================="
    echo "🛑 天气订阅系统停止脚本"
    echo "=========================================="
    
    # 显示当前进程
    show_running_processes
    echo ""
    
    # 停止各个服务
    stop_service "Django" "logs/django.pid" "python.*manage.py.*runserver"
    stop_service "Celery Worker" "logs/celery_worker.pid" "celery.*worker"
    stop_service "Celery Beat" "logs/celery_beat.pid" "celery.*beat"
    
    # 清理PID文件
    cleanup_logs
    
    echo ""
    
    # 显示最终状态
    show_final_status
    
    echo ""
    log_info "如需重新启动服务，请运行: ./start_services.sh"
}

# 运行主函数
main "$@"
