#!/bin/bash

# 天气订阅系统状态检查脚本
# 使用方法: chmod +x check_status.sh && ./check_status.sh

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

# 检查服务状态
check_service_status() {
    local service_name=$1
    local process_pattern=$2
    local pid_file=$3
    
    local pids=$(pgrep -f "$process_pattern")
    local pid_count=$(echo "$pids" | grep -c .)
    
    if [[ $pid_count -gt 0 ]]; then
        echo -e "$service_name: ${GREEN}运行中${NC} ($pid_count 个进程)"
        if [[ -n "$pids" ]]; then
            echo "   PID: $pids"
        fi
        
        # 检查PID文件
        if [[ -n "$pid_file" && -f "$pid_file" ]]; then
            local stored_pid=$(cat "$pid_file")
            if echo "$pids" | grep -q "$stored_pid"; then
                echo -e "   PID文件: ${GREEN}正确${NC} ($stored_pid)"
            else
                echo -e "   PID文件: ${YELLOW}不匹配${NC} (存储: $stored_pid, 实际: $pids)"
            fi
        fi
        return 0
    else
        echo -e "$service_name: ${RED}未运行${NC}"
        return 1
    fi
}

# 检查Redis连接
check_redis() {
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping &> /dev/null; then
            echo -e "Redis: ${GREEN}运行中${NC}"
            
            # 获取Redis信息
            local redis_info=$(redis-cli info server 2>/dev/null | grep "redis_version" | cut -d: -f2 | tr -d '\r')
            if [[ -n "$redis_info" ]]; then
                echo "   版本: $redis_info"
            fi
            
            # 检查连接数
            local connected_clients=$(redis-cli info clients 2>/dev/null | grep "connected_clients" | cut -d: -f2 | tr -d '\r')
            if [[ -n "$connected_clients" ]]; then
                echo "   连接数: $connected_clients"
            fi
            
            return 0
        else
            echo -e "Redis: ${RED}无法连接${NC}"
            return 1
        fi
    else
        echo -e "Redis: ${RED}未安装${NC}"
        return 1
    fi
}

# 检查数据库连接
check_database() {
    if [[ -d "venv" ]]; then
        source venv/bin/activate
        
        if python manage.py check --database default &> /dev/null; then
            echo -e "数据库: ${GREEN}连接正常${NC}"
            
            # 获取数据库信息
            local db_info=$(python -c "
from django.conf import settings
import django
django.setup()
db = settings.DATABASES['default']
print(f\"{db['ENGINE'].split('.')[-1]} - {db['NAME']}@{db['HOST']}:{db['PORT']}\")
" 2>/dev/null)
            
            if [[ -n "$db_info" ]]; then
                echo "   配置: $db_info"
            fi
            
            return 0
        else
            echo -e "数据库: ${RED}连接失败${NC}"
            return 1
        fi
    else
        echo -e "数据库: ${RED}虚拟环境不存在${NC}"
        return 1
    fi
}

# 检查定时任务
check_periodic_tasks() {
    if [[ -d "venv" ]]; then
        source venv/bin/activate
        
        local task_count=$(python -c "
import django
django.setup()
from django_celery_beat.models import PeriodicTask
print(PeriodicTask.objects.filter(enabled=True).count())
" 2>/dev/null)
        
        if [[ -n "$task_count" && "$task_count" -gt 0 ]]; then
            echo -e "定时任务: ${GREEN}已配置${NC} ($task_count 个启用)"
            
            # 显示任务详情
            python -c "
import django
django.setup()
from django_celery_beat.models import PeriodicTask
tasks = PeriodicTask.objects.filter(enabled=True)
for task in tasks:
    print(f'   - {task.name}: {task.task}')
" 2>/dev/null
            
            return 0
        else
            echo -e "定时任务: ${YELLOW}未配置${NC}"
            return 1
        fi
    else
        echo -e "定时任务: ${RED}无法检查${NC}"
        return 1
    fi
}

# 检查日志文件
check_logs() {
    echo "日志文件状态:"
    
    local log_files=("logs/django.log" "logs/celery_worker.log" "logs/celery_beat.log")
    
    for log_file in "${log_files[@]}"; do
        if [[ -f "$log_file" ]]; then
            local size=$(du -h "$log_file" | cut -f1)
            local lines=$(wc -l < "$log_file")
            echo -e "   $(basename "$log_file"): ${GREEN}存在${NC} (大小: $size, 行数: $lines)"
        else
            echo -e "   $(basename "$log_file"): ${YELLOW}不存在${NC}"
        fi
    done
}

# 检查网络端口
check_ports() {
    echo "端口监听状态:"
    
    # 检查Django端口
    if netstat -tuln 2>/dev/null | grep -q ":8001 "; then
        echo -e "   8001 (Django): ${GREEN}监听中${NC}"
    else
        echo -e "   8001 (Django): ${RED}未监听${NC}"
    fi
    
    # 检查Redis端口
    if netstat -tuln 2>/dev/null | grep -q ":6379 "; then
        echo -e "   6379 (Redis): ${GREEN}监听中${NC}"
    else
        echo -e "   6379 (Redis): ${RED}未监听${NC}"
    fi
}

# 显示系统资源
show_system_resources() {
    echo "系统资源使用:"
    
    # CPU使用率
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    echo "   CPU使用率: ${cpu_usage}%"
    
    # 内存使用率
    local mem_info=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
    echo "   内存使用率: ${mem_info}%"
    
    # 磁盘使用率
    local disk_usage=$(df -h . | awk 'NR==2{print $5}')
    echo "   磁盘使用率: $disk_usage"
}

# 主函数
main() {
    echo "=========================================="
    echo "📊 天气订阅系统状态检查"
    echo "=========================================="
    
    local all_good=true
    
    echo "🔍 服务状态检查:"
    echo "----------------------------------------"
    
    # 检查各个服务
    if ! check_service_status "Django" "python.*manage.py.*runserver" "logs/django.pid"; then
        all_good=false
    fi
    
    if ! check_service_status "Celery Worker" "celery.*worker" "logs/celery_worker.pid"; then
        all_good=false
    fi
    
    if ! check_service_status "Celery Beat" "celery.*beat" "logs/celery_beat.pid"; then
        all_good=false
    fi
    
    if ! check_redis; then
        all_good=false
    fi
    
    echo ""
    echo "🔍 连接状态检查:"
    echo "----------------------------------------"
    
    if ! check_database; then
        all_good=false
    fi
    
    check_periodic_tasks
    
    echo ""
    echo "🔍 系统状态检查:"
    echo "----------------------------------------"
    
    check_logs
    echo ""
    check_ports
    echo ""
    show_system_resources
    
    echo ""
    echo "=========================================="
    
    if $all_good; then
        log_success "所有核心服务运行正常！"
        echo ""
        echo "📱 访问地址:"
        echo "   网站首页: http://$(hostname -I | awk '{print $1}'):8001/"
        echo "   管理后台: http://$(hostname -I | awk '{print $1}'):8001/admin/"
    else
        log_warning "部分服务存在问题，请检查上述状态"
        echo ""
        echo "🔧 修复建议:"
        echo "   重启服务: ./start_services.sh"
        echo "   查看日志: tail -f logs/*.log"
    fi
    
    echo "=========================================="
}

# 运行主函数
main "$@"
