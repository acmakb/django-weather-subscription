# 🌤️ Django 天气订阅系统

一个基于 Django 的智能天气订阅系统，支持用户注册、城市天气订阅、每日定时邮件推送等功能。

## 📋 项目简介

本系统允许用户注册账号，订阅感兴趣城市的天气信息，并在每天早上6点自动接收天气预报邮件。系统采用现代化的Web技术栈，具有完善的管理后台和用户界面。

## ✨ 主要功能

### 🔐 用户系统
- 用户注册/登录（支持邮箱登录）
- 邮箱验证功能
- 用户个人中心
- 密码重置

### 🌍 天气订阅
- 三级城市选择（省/市/区县）
- 多城市订阅管理
- 订阅状态控制（激活/停用）
- 订阅历史记录

### 📧 邮件系统
- 每日定时天气邮件推送（早上6点）
- 精美的HTML邮件模板
- 邮件发送日志记录
- 测试邮件功能

### 🎛️ 管理后台
- 现代化的SimpleUI界面
- 用户管理
- 城市数据管理
- 订阅管理（支持批量操作）
- 邮件日志查看
- 系统统计面板

### ⚡ 异步任务
- Celery异步任务处理
- Redis消息队列
- 定时任务调度
- 任务监控

## 🛠️ 技术栈

### 后端技术
- **Django 4.2.7** - Web框架
- **Python 3.11** - 编程语言
- **MySQL** - 数据库
- **Redis** - 缓存和消息队列
- **Celery** - 异步任务处理
- **django-celery-beat** - 定时任务

### 前端技术
- **Bootstrap 5** - UI框架
- **SimpleUI** - Django管理后台美化
- **JavaScript/jQuery** - 前端交互
- **HTML5/CSS3** - 页面结构和样式

### 第三方服务
- **高德地图API** - 天气数据获取
- **QQ邮箱SMTP** - 邮件发送服务

### 开发工具
- **PyMySQL** - MySQL数据库连接
- **Pandas** - 数据处理
- **Requests** - HTTP请求
- **python-dotenv** - 环境变量管理

## 📁 项目结构

```
weatherblog/
├── accounts/                 # 用户账户模块
│   ├── models.py            # 用户模型
│   ├── views.py             # 用户视图
│   ├── forms.py             # 用户表单
│   └── urls.py              # 用户路由
├── weather/                  # 天气模块
│   ├── models.py            # 城市和天气数据模型
│   ├── services.py          # 天气API服务
│   ├── views.py             # 天气视图
│   └── management/          # 数据导入命令
├── subscriptions/            # 订阅模块
│   ├── models.py            # 订阅和邮件日志模型
│   ├── views.py             # 订阅视图
│   ├── forms.py             # 订阅表单
│   ├── tasks.py             # Celery异步任务
│   ├── email_service.py     # 邮件发送服务
│   └── admin.py             # 管理后台配置
├── templates/                # 模板文件
│   ├── base.html            # 基础模板
│   ├── accounts/            # 用户模板
│   ├── weather/             # 天气模板
│   ├── subscriptions/       # 订阅模板
│   └── emails/              # 邮件模板
├── static/                   # 静态文件
├── weatherblog/              # 项目配置
│   ├── settings.py          # 开发环境配置
│   ├── settings_production.py # 生产环境配置
│   ├── celery.py            # Celery配置
│   └── urls.py              # 主路由配置
├── requirements.txt          # 依赖包列表
├── manage.py                # Django管理脚本
└── AMap_adcode_citycode.xlsx # 城市数据文件
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- MySQL 5.7+
- Redis 6.0+
- Git

### 1. 克隆项目

```bash
git clone https://github.com/acmakb/django-weather-subscription.git
cd django-weather-subscription
```

### 2. 创建虚拟环境

```bash
# 使用conda（推荐）
conda create -n weather python=3.11
conda activate weather

# 或使用venv
python -m venv weather_env
source weather_env/bin/activate  # Linux/Mac
# weather_env\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置数据库

创建MySQL数据库：
```sql
CREATE DATABASE weatherblog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. 配置环境变量

修改 `weatherblog/settings.py` 中的配置：

```python
# 数据库配置
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "weatherblog",
        "USER": "your_mysql_user",
        "PASSWORD": "your_mysql_password",
        "HOST": "localhost",
        "PORT": "3306",
    }
}

# 邮箱配置
EMAIL_HOST_USER = 'your_email@qq.com'
EMAIL_HOST_PASSWORD = 'your_email_auth_code'
DEFAULT_FROM_EMAIL = 'your_email@qq.com'

# 高德地图API密钥
WEATHER_API_KEY = 'your_amap_api_key'
```

### 6. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. 导入城市数据

```bash
python manage.py import_cities
```

### 8. 创建超级用户

```bash
python manage.py createsuperuser
```

### 9. 启动服务

#### 开发环境（简单启动）
```bash
# 启动Django
python manage.py runserver 0.0.0.0:8001

# 新终端启动Redis
redis-server

# 新终端启动Celery Worker
celery -A weatherblog worker -l info

# 新终端启动Celery Beat
celery -A weatherblog beat -l info
```

#### 生产环境（后台运行）
```bash
# 启动Redis
sudo systemctl start redis

# 启动Django
nohup python manage.py runserver 0.0.0.0:8001 > logs/django.log 2>&1 &

# 启动Celery Worker
nohup celery -A weatherblog worker -l info > logs/celery_worker.log 2>&1 &

# 启动Celery Beat
nohup celery -A weatherblog beat -l info > logs/celery_beat.log 2>&1 &
```

### 10. 访问系统

- 前台用户界面: http://localhost:8001
- 管理后台: http://localhost:8001/admin

## ⚙️ 配置说明

### 必需配置项

#### 1. 高德地图API密钥
1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册账号并创建应用
3. 获取Web服务API密钥
4. 在 `settings.py` 中配置 `WEATHER_API_KEY`

#### 2. QQ邮箱SMTP配置
1. 登录QQ邮箱，进入设置
2. 开启SMTP服务
3. 获取授权码
4. 在 `settings.py` 中配置邮箱信息

#### 3. MySQL数据库
1. 安装MySQL服务器
2. 创建数据库和用户
3. 在 `settings.py` 中配置数据库连接

#### 4. Redis服务
1. 安装Redis服务器
2. 启动Redis服务
3. 确保端口6379可访问

### 可选配置项

#### 生产环境配置
使用 `settings_production.py` 进行生产环境部署：

```bash
export DJANGO_SETTINGS_MODULE=weatherblog.settings_production
export SECRET_KEY="your-very-secure-secret-key"
export DEBUG=False
export ALLOWED_HOSTS="your-domain.com,www.your-domain.com"
export DB_PASSWORD="your-db-password"
export EMAIL_PASSWORD="your-email-auth-code"
export WEATHER_API_KEY="your-amap-api-key"
```

## 📊 功能特性

### 邮件模板
- 响应式HTML邮件设计
- 包含当前天气和4天预报
- 支持测试邮件功能
- 邮件发送状态追踪

### 管理后台功能
- **用户管理**: 查看、编辑用户信息，管理邮箱验证状态
- **城市管理**: 管理三级城市数据，支持批量导入
- **订阅管理**: 
  - 查看所有订阅记录
  - 批量激活/停用订阅
  - 单个订阅状态切换
  - 发送测试邮件
- **邮件日志**: 查看邮件发送历史和状态
- **系统统计**: 用户数量、订阅统计等

### 定时任务
- 每日早上6点自动发送天气邮件
- 自动清理30天前的邮件日志
- 支持手动触发任务测试

## 🔧 开发指南

### 添加新功能
1. 在相应的app中创建模型、视图、表单
2. 配置URL路由
3. 创建模板文件
4. 更新管理后台配置
5. 编写测试用例

### 自定义邮件模板
编辑 `templates/emails/` 目录下的模板文件：
- `weather_report.html` - HTML邮件模板
- `weather_report.txt` - 纯文本邮件模板

### 添加新的定时任务
在 `subscriptions/tasks.py` 中定义新任务，然后在Django管理后台的"定时任务"中配置执行计划。

## 🐛 故障排除

### 常见问题

1. **邮件发送失败**
   - 检查QQ邮箱SMTP配置
   - 确认授权码正确
   - 检查网络连接
   - 测试命令: `python test_email_task.py`

2. **Celery任务不执行**
   - 确认Redis服务运行正常
   - 检查Celery Worker和Beat进程状态
   - 查看Celery日志
   - 测试命令: `python manage.py shell` 然后 `from subscriptions.tasks import test_celery_task; test_celery_task.delay()`

3. **数据库连接错误**
   - 检查MySQL服务状态
   - 确认数据库配置正确
   - 检查PyMySQL安装
   - 测试命令: `python test_mysql_connection.py`

4. **城市数据导入失败**
   - 确认Excel文件路径正确
   - 检查文件格式和内容
   - 查看导入命令输出
   - 重新运行: `python manage.py import_cities`

5. **管理后台订阅切换按钮无响应**
   - 检查JavaScript文件是否正确加载
   - 确认URL配置正确
   - 查看浏览器控制台错误信息

### 服务状态检查
```bash
# 检查所有服务状态
./check_status.sh

# 手动检查各服务
ps aux | grep python  # 检查Django进程
ps aux | grep celery  # 检查Celery进程
redis-cli ping        # 检查Redis连接
mysql -u root -p -e "SELECT 1"  # 检查MySQL连接
```

### 日志查看
```bash
# Django日志
tail -f logs/django.log

# Celery Worker日志
tail -f logs/celery_worker.log

# Celery Beat日志
tail -f logs/celery_beat.log

# 系统日志
tail -f weather.log
```

### 重启服务
```bash
# 停止所有服务
./stop_services.sh

# 启动所有服务
./start_services.sh

# 或手动重启
pkill -f "python.*manage.py.*runserver"
pkill -f "celery.*worker"
pkill -f "celery.*beat"

# 重新启动
nohup python manage.py runserver 0.0.0.0:8001 > logs/django.log 2>&1 &
nohup celery -A weatherblog worker -l info > logs/celery_worker.log 2>&1 &
nohup celery -A weatherblog beat -l info > logs/celery_beat.log 2>&1 &
```

## 🔒 安全注意事项

### 生产环境安全配置

1. **更改默认密钥**
   ```python
   # 生成新的SECRET_KEY
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

2. **数据库安全**
   - 使用强密码
   - 限制数据库访问权限
   - 定期备份数据

3. **邮箱安全**
   - 使用专用邮箱账号
   - 定期更换授权码
   - 监控邮件发送量

4. **API密钥安全**
   - 不要在代码中硬编码API密钥
   - 使用环境变量存储敏感信息
   - 定期轮换API密钥

5. **服务器安全**
   - 配置防火墙
   - 使用HTTPS
   - 定期更新系统和依赖包

## 📈 性能优化

### 数据库优化
- 为常用查询字段添加索引
- 使用数据库连接池
- 定期清理过期数据

### 缓存优化
- 使用Redis缓存天气数据
- 缓存用户会话信息
- 静态文件CDN加速

### 任务优化
- 合理设置Celery并发数
- 监控任务执行时间
- 优化邮件发送批次

## 🚀 部署建议

### Docker部署
```dockerfile
# Dockerfile示例
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
```

### Nginx配置
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/your/static/files/;
    }
}
```

### 系统服务配置
```ini
# /etc/systemd/system/weatherblog.service
[Unit]
Description=Weather Blog Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/weatherblog
ExecStart=/path/to/venv/bin/python manage.py runserver 0.0.0.0:8001
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📊 系统截图

### 用户界面
- 🏠 **首页**: 简洁的天气查询界面
- 📝 **注册/登录**: 用户友好的认证界面
- ⚙️ **个人中心**: 订阅管理和个人信息
- 🌍 **订阅页面**: 三级城市选择界面

### 管理后台
- 📈 **系统概览**: 用户和订阅统计
- 👥 **用户管理**: 用户信息和状态管理
- 🏙️ **城市管理**: 城市数据维护
- 📧 **订阅管理**: 订阅状态和批量操作
- 📋 **邮件日志**: 发送历史和状态追踪

## 🧪 测试功能

### 单元测试
```bash
# 运行所有测试
python manage.py test

# 运行特定应用测试
python manage.py test accounts
python manage.py test weather
python manage.py test subscriptions
```

### 功能测试脚本
```bash
# 测试邮件发送
python test_email_task.py

# 测试数据库连接
python test_mysql_connection.py

# 测试Celery任务
python manage.py shell
>>> from subscriptions.tasks import test_celery_task
>>> test_celery_task.delay()
```

### API测试
```bash
# 测试天气API
curl "http://localhost:8001/weather/api/current/?city=北京"

# 测试用户API
curl -X POST "http://localhost:8001/accounts/api/register/" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

## 📝 更新日志

### v1.0.0 (2025-01-XX)
- ✅ 完整的用户注册登录系统
- ✅ 三级城市选择和天气订阅
- ✅ 每日定时邮件推送
- ✅ 现代化管理后台
- ✅ 异步任务处理
- ✅ 邮件模板和日志系统
- ✅ 批量操作功能
- ✅ 生产环境配置
- ✅ 订阅状态实时切换
- ✅ 测试邮件功能
- ✅ 完善的错误处理

## 🔮 未来计划

### 短期计划 (v1.1)
- [ ] 微信小程序支持
- [ ] 短信通知功能
- [ ] 天气预警推送
- [ ] 用户偏好设置
- [ ] 邮件模板自定义

### 中期计划 (v1.2)
- [ ] 移动端APP
- [ ] 多语言支持
- [ ] 天气数据可视化
- [ ] 社交分享功能
- [ ] 订阅统计分析

### 长期计划 (v2.0)
- [ ] AI天气预测
- [ ] 个性化推荐
- [ ] 企业版功能
- [ ] 开放API平台
- [ ] 插件系统

## 💡 使用技巧

### 管理后台技巧
1. **批量操作**: 选中多个订阅后，使用顶部的操作下拉菜单
2. **快速搜索**: 使用搜索框快速定位用户或城市
3. **过滤器**: 使用右侧过滤器按状态、时间等条件筛选
4. **导出数据**: 在操作菜单中选择导出功能

### 开发技巧
1. **调试模式**: 设置 `DEBUG=True` 查看详细错误信息
2. **日志级别**: 调整日志级别获取更多调试信息
3. **数据库查询**: 使用Django Debug Toolbar监控SQL查询
4. **缓存清理**: 定期清理Redis缓存避免内存溢出

### 运维技巧
1. **监控脚本**: 使用 `check_status.sh` 定期检查服务状态
2. **自动重启**: 配置systemd服务实现自动重启
3. **日志轮转**: 配置logrotate避免日志文件过大
4. **备份策略**: 定期备份数据库和重要配置文件

## 📞 技术支持

### 问题反馈
- 🐛 **Bug报告**: [GitHub Issues](https://github.com/acmakb/django-weather-subscription/issues)
- 💡 **功能建议**: [GitHub Discussions](https://github.com/acmakb/django-weather-subscription/discussions)
- 📧 **邮件联系**: 18654693179@163.com

### 文档资源
- 📖 **Django官方文档**: https://docs.djangoproject.com/
- 🔄 **Celery文档**: https://docs.celeryproject.org/
- 🗺️ **高德地图API**: https://lbs.amap.com/api/
- 🎨 **SimpleUI文档**: https://github.com/newpanjing/simpleui

### 社区支持
- 💬 **QQ**: 1480647675
- 🌐 **官方网站**: http://www.acmakb.top/

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👨‍💻 作者

- **acmakb** - *Initial work* - [YourGitHub](https://github.com/acmakb)

## 🙏 致谢

- [Django](https://www.djangoproject.com/) - Web框架
- [高德地图](https://lbs.amap.com/) - 天气数据API
- [SimpleUI](https://github.com/newpanjing/simpleui) - Django管理后台美化
- [Celery](https://docs.celeryproject.org/) - 异步任务处理

---

如果这个项目对你有帮助，请给个 ⭐ Star！
