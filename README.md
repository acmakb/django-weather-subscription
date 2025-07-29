# 🌤️ Django 天气订阅系统

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/yourusername/django-weather-subscription.svg)](https://github.com/yourusername/django-weather-subscription/stargazers)

> 一个功能完整的Django天气订阅系统，支持用户注册、城市订阅、定时邮件推送和现代化管理后台。

## ✨ 主要特性

🔐 **完整用户系统** - 注册/登录、邮箱验证、密码重置  
🌍 **智能城市选择** - 三级联动选择（省/市/区县）  
📧 **定时邮件推送** - 每日6点自动发送天气预报  
🎛️ **现代化后台** - SimpleUI美化的管理界面  
⚡ **异步任务处理** - Celery + Redis 高性能处理  
📊 **数据统计分析** - 用户订阅数据可视化  

## 🚀 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone https://github.com/acmakb/django-weather-subscription.git
cd django-weather-subscription

# 创建虚拟环境
conda create -n weather python=3.11
conda activate weather

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置数据库
```sql
-- 创建MySQL数据库
CREATE DATABASE weatherblog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 修改配置
编辑 `weatherblog/settings.py`：
```python
# 数据库配置
DATABASES = {
    "default": {
        "NAME": "weatherblog",
        "USER": "your_mysql_user",
        "PASSWORD": "your_mysql_password",
        # ...
    }
}

# 邮箱配置（QQ邮箱）
EMAIL_HOST_USER = 'your_email@qq.com'
EMAIL_HOST_PASSWORD = 'your_qq_auth_code'  # QQ邮箱授权码

# 高德地图API密钥
WEATHER_API_KEY = 'your_amap_api_key'
```

### 4. 初始化系统
```bash
# 数据库迁移
python manage.py migrate

# 导入城市数据
python manage.py import_cities

# 创建管理员
python manage.py createsuperuser
```

### 5. 启动服务
```bash
# 启动Redis
redis-server

# 启动Django（新终端）
python manage.py runserver 0.0.0.0:8001

# 启动Celery Worker（新终端）
celery -A weatherblog worker -l info

# 启动Celery Beat（新终端）
celery -A weatherblog beat -l info
```

### 6. 访问系统
- 🌐 **用户界面**: http://localhost:8001
- 🛠️ **管理后台**: http://localhost:8001/admin

## 🛠️ 技术栈

| 类别 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **后端** | Django | 4.2.7 | Web框架 |
| **数据库** | MySQL | 5.7+ | 主数据库 |
| **缓存** | Redis | 6.0+ | 消息队列&缓存 |
| **任务队列** | Celery | 5.3.4 | 异步任务处理 |
| **前端** | Bootstrap | 5.x | UI框架 |
| **管理后台** | SimpleUI | 2025.6.24 | Django后台美化 |
| **API服务** | 高德地图API | - | 天气数据源 |

## 📁 项目结构

```
weatherblog/
├── 📁 accounts/          # 用户账户模块
├── 📁 weather/           # 天气数据模块  
├── 📁 subscriptions/     # 订阅管理模块
├── 📁 templates/         # 模板文件
├── 📁 static/           # 静态资源
├── 📁 weatherblog/      # 项目配置
├── 📄 requirements.txt   # 依赖列表
├── 📄 manage.py         # Django管理脚本
└── 📄 AMap_adcode_citycode.xlsx  # 城市数据
```

## 🎯 核心功能

### 👤 用户系统
- ✅ 邮箱注册/登录
- ✅ 邮箱验证机制
- ✅ 密码重置功能
- ✅ 用户个人中心

### 🌦️ 天气订阅
- ✅ 三级城市联动选择
- ✅ 多城市订阅管理
- ✅ 订阅状态控制
- ✅ 历史记录查看

### 📬 邮件系统
- ✅ 精美HTML邮件模板
- ✅ 每日定时推送（6:00AM）
- ✅ 邮件发送日志
- ✅ 测试邮件功能

### 🎛️ 管理后台
- ✅ 用户管理
- ✅ 订阅管理（支持批量操作）
- ✅ 城市数据管理
- ✅ 邮件日志查看
- ✅ 系统统计面板

## ⚙️ 配置指南

### 🔑 必需配置

#### 高德地图API
1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册并创建应用
3. 获取Web服务API Key
4. 配置到 `WEATHER_API_KEY`

#### QQ邮箱SMTP
1. 登录QQ邮箱 → 设置 → 账户
2. 开启SMTP服务
3. 获取授权码
4. 配置邮箱信息

#### MySQL数据库
```bash
# 安装MySQL
sudo apt install mysql-server  # Ubuntu
brew install mysql             # macOS

# 创建数据库
mysql -u root -p
CREATE DATABASE weatherblog CHARACTER SET utf8mb4;
```

#### Redis服务
```bash
# 安装Redis
sudo apt install redis-server  # Ubuntu
brew install redis             # macOS

# 启动服务
redis-server
```

## 🚀 生产部署

### 环境变量配置
```bash
export DJANGO_SETTINGS_MODULE=weatherblog.settings_production
export SECRET_KEY="your-very-secure-secret-key"
export DEBUG=False
export ALLOWED_HOSTS="your-domain.com"
export DB_PASSWORD="your-db-password"
export EMAIL_PASSWORD="your-email-auth-code"
export WEATHER_API_KEY="your-amap-api-key"
```

### 后台运行
```bash
# 启动所有服务
nohup python manage.py runserver 0.0.0.0:8001 > logs/django.log 2>&1 &
nohup celery -A weatherblog worker -l info > logs/celery_worker.log 2>&1 &
nohup celery -A weatherblog beat -l info > logs/celery_beat.log 2>&1 &
```

### 服务管理脚本
```bash
# 启动服务
./start_services.sh

# 停止服务  
./stop_services.sh

# 检查状态
./check_status.sh
```

## 🔧 开发指南

### 本地开发
```bash
# 开启调试模式
export DEBUG=True

# 运行开发服务器
python manage.py runserver

# 实时监控日志
tail -f logs/django.log
```

### 测试功能
```bash
# 运行测试
python manage.py test

# 测试邮件发送
python test_email_task.py

# 测试数据库连接
python test_mysql_connection.py
```

## 🐛 常见问题

<details>
<summary><strong>邮件发送失败</strong></summary>

- 检查QQ邮箱SMTP配置
- 确认授权码正确
- 运行测试: `python test_email_task.py`
</details>

<details>
<summary><strong>Celery任务不执行</strong></summary>

- 确认Redis服务运行: `redis-cli ping`
- 检查Celery进程: `ps aux | grep celery`
- 查看日志: `tail -f logs/celery_worker.log`
</details>

<details>
<summary><strong>数据库连接错误</strong></summary>

- 检查MySQL服务: `systemctl status mysql`
- 测试连接: `python test_mysql_connection.py`
- 确认配置正确
</details>

## 📊 系统特色

### 🎨 现代化界面
- 响应式设计，支持移动端
- SimpleUI美化的管理后台
- Bootstrap 5 现代化UI组件

### ⚡ 高性能架构
- Celery异步任务处理
- Redis缓存加速
- 数据库查询优化

### 🔒 安全可靠
- CSRF保护
- SQL注入防护
- 邮箱验证机制
- 密码加密存储

### 📈 可扩展性
- 模块化设计
- 插件化架构
- 易于二次开发

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 提交 Pull Request

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证。

## 🙏 致谢

- [Django](https://www.djangoproject.com/) - 优秀的Web框架
- [高德地图](https://lbs.amap.com/) - 可靠的天气数据API
- [SimpleUI](https://github.com/newpanjing/simpleui) - 美观的Django后台
- [Celery](https://docs.celeryproject.org/) - 强大的异步任务队列

---

⭐ 如果这个项目对你有帮助，请给个 Star！

📧 问题反馈: [GitHub Issues](https://github.com/acmakb/django-weather-subscription/issues)
