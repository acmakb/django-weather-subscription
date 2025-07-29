# 天气订阅系统简单部署指南

## 🚨 问题诊断

您遇到的问题是：**只启动了Django应用，但没有启动Celery服务**！

定时邮件发送功能需要以下服务同时运行：
- ✅ **Django应用** - 已启动 (runserver)
- ❌ **Celery Worker** - 未启动 (处理异步任务)
- ❌ **Celery Beat** - 未启动 (定时任务调度)
- ❌ **Redis服务** - 需要确认是否运行

## 🔧 快速解决方案

### 1. 停止当前服务
```bash
# 停止当前的Django服务
pkill -f "python.*manage.py.*runserver"

# 或者使用我们的停止脚本
chmod +x stop_services.sh
./stop_services.sh
```

### 2. 检查Redis服务
```bash
# 检查Redis是否安装和运行
redis-cli ping

# 如果没有安装Redis
sudo apt install redis-server

# 启动Redis服务
sudo systemctl start redis
sudo systemctl enable redis
```

### 3. 使用完整启动脚本
```bash
# 给脚本执行权限
chmod +x start_services.sh
chmod +x stop_services.sh
chmod +x check_status.sh

# 启动所有服务
./start_services.sh
```

### 4. 检查服务状态
```bash
# 检查所有服务状态
./check_status.sh
```

### 5. 测试邮件功能
```bash
# 测试邮件发送功能
python test_email_task.py
```

## 📁 脚本文件说明

### 🚀 `start_services.sh` - 启动所有服务
- 自动检查环境依赖
- 启动Django、Celery Worker、Celery Beat
- 设置定时任务
- 显示服务状态

### 🛑 `stop_services.sh` - 停止所有服务
- 优雅停止所有相关进程
- 清理PID文件
- 显示最终状态

### 📊 `check_status.sh` - 检查服务状态
- 检查所有服务运行状态
- 检查数据库和Redis连接
- 显示系统资源使用情况
- 检查定时任务配置

### 🧪 `test_email_task.py` - 测试邮件功能
- 测试Redis和Celery连接
- 测试邮件配置
- 手动执行邮件发送任务
- 检查定时任务设置

## 🔍 故障排除

### 1. Redis连接问题
```bash
# 检查Redis状态
sudo systemctl status redis

# 重启Redis
sudo systemctl restart redis

# 测试连接
redis-cli ping
```

### 2. Celery连接问题
```bash
# 查看Celery Worker日志
tail -f logs/celery_worker.log

# 查看Celery Beat日志
tail -f logs/celery_beat.log

# 重启Celery服务
./stop_services.sh
./start_services.sh
```

### 3. 邮件发送问题
```bash
# 测试邮件配置
python test_email_task.py

# 检查QQ邮箱设置
# 确保授权码正确: qglblrluavuzijcg
# 确保开启了SMTP服务
```

### 4. 定时任务问题
```bash
# 检查定时任务设置
python manage.py shell
```

```python
from django_celery_beat.models import PeriodicTask
tasks = PeriodicTask.objects.filter(enabled=True)
for task in tasks:
    print(f"{task.name}: {task.crontab}")
```

## 📝 正确的启动流程

### 完整启动命令
```bash
# 1. 确保Redis运行
sudo systemctl start redis

# 2. 启动所有服务
./start_services.sh

# 3. 检查状态
./check_status.sh

# 4. 测试邮件功能
python test_email_task.py
```

### 手动启动命令（如果脚本有问题）
```bash
# 激活虚拟环境
source venv/bin/activate

# 创建日志目录
mkdir -p logs

# 启动Django (终端1)
nohup python manage.py runserver 0.0.0.0:8001 > logs/django.log 2>&1 &

# 启动Celery Worker (终端2)
nohup celery -A weatherblog worker -l info > logs/celery_worker.log 2>&1 &

# 启动Celery Beat (终端3)
nohup celery -A weatherblog beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler > logs/celery_beat.log 2>&1 &

# 设置定时任务
python manage.py setup_periodic_tasks
```

## 🕕 定时任务说明

系统会在每天早上6点自动发送天气邮件：
- **任务名称**: 每日天气邮件发送
- **执行时间**: 每天 06:00 (Asia/Shanghai时区)
- **任务函数**: `subscriptions.tasks.send_daily_weather_emails`

## 📊 监控和日志

### 日志文件位置
```bash
logs/django.log          # Django应用日志
logs/celery_worker.log   # Celery Worker日志
logs/celery_beat.log     # Celery Beat日志
```

### 实时查看日志
```bash
# 查看所有日志
tail -f logs/*.log

# 查看特定日志
tail -f logs/celery_beat.log
```

### 检查邮件发送记录
在管理后台查看：
- 访问: `http://your-ip:8001/admin/`
- 进入: 订阅管理 -> 邮件日志

## 🎯 验证邮件功能

### 1. 立即测试
```bash
# 手动触发邮件发送
python test_email_task.py
```

### 2. 等待定时发送
- 确保所有服务运行正常
- 等待明天早上6点
- 检查邮件日志记录

### 3. 检查发送结果
- 查看 `logs/celery_beat.log` 中的定时任务执行记录
- 查看 `logs/celery_worker.log` 中的邮件发送记录
- 在管理后台查看邮件日志

## 🔄 日常维护

### 启动服务
```bash
./start_services.sh
```

### 停止服务
```bash
./stop_services.sh
```

### 检查状态
```bash
./check_status.sh
```

### 重启服务
```bash
./stop_services.sh
./start_services.sh
```

## 🎉 成功标志

当您看到以下状态时，说明配置成功：

```
📊 天气订阅系统状态检查
==========================================
🔍 服务状态检查:
----------------------------------------
Django: 运行中 (1 个进程)
Celery Worker: 运行中 (1 个进程)
Celery Beat: 运行中 (1 个进程)
Redis: 运行中

🔍 连接状态检查:
----------------------------------------
数据库: 连接正常
定时任务: 已配置 (1 个启用)
   - 每日天气邮件发送: subscriptions.tasks.send_daily_weather_emails

✅ 所有核心服务运行正常！
```

现在您的天气订阅系统应该能够正常发送定时邮件了！🎉
