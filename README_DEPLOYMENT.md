# 天气订阅系统部署指南

## 📁 部署文件说明

本项目包含以下部署相关文件：

### 📄 核心文件
- **`DEPLOYMENT.md`** - 详细的Linux部署文档，包含完整的部署步骤
- **`requirements.txt`** - Python依赖包列表 (使用PyMySQL替代mysqlclient)
- **`deploy.sh`** - 自动化部署脚本
- **`weatherblog/settings_production.py`** - 生产环境配置文件
- **`test_mysql_connection.py`** - MySQL连接测试脚本

### 🚀 快速部署

#### 方法一：使用自动化脚本（推荐）
```bash
# 1. 克隆项目到服务器
git clone <your-repo-url> weatherblog
cd weatherblog

# 2. 给部署脚本执行权限
chmod +x deploy.sh

# 3. 运行部署脚本
./deploy.sh

# 4. 按照提示完成后续配置
```

#### 方法二：手动部署
请参考 `DEPLOYMENT.md` 文档中的详细步骤。

### 🔧 部署后配置

#### 1. 编辑环境变量
```bash
vim .env
```
根据您的实际环境修改配置参数。

#### 2. 创建数据库
```sql
-- 登录MySQL
mysql -u root -p

-- 创建数据库
CREATE DATABASE weatherblog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户并授权
CREATE USER 'weatherapp'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON weatherblog.* TO 'weatherapp'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3. 测试数据库连接（推荐）
```bash
# 测试PyMySQL连接
python test_mysql_connection.py
```

#### 4. 创建超级用户
```bash
source venv/bin/activate
python manage.py createsuperuser
```

#### 5. 导入城市数据（如果需要）
```bash
python manage.py shell
```

### 📊 服务管理

#### 查看服务状态
```bash
sudo supervisorctl status
```

#### 重启服务
```bash
# 重启Django应用
sudo supervisorctl restart weatherblog

# 重启Celery
sudo supervisorctl restart celery
sudo supervisorctl restart celerybeat

# 重启Nginx
sudo systemctl restart nginx
```

#### 查看日志
```bash
# Django日志
tail -f logs/django.log

# Gunicorn日志
tail -f logs/gunicorn.log

# Celery日志
tail -f logs/celery.log

# Nginx日志
sudo tail -f /var/log/nginx/error.log
```

### 🔒 安全配置

#### 1. 配置防火墙
```bash
# Ubuntu/Debian
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

#### 2. 配置SSL证书（推荐）
```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 🎯 功能测试

#### 1. 网站访问测试
- 前台页面: `http://your-server-ip/`
- 管理后台: `http://your-server-ip/admin/`

#### 2. 邮件发送测试
```bash
python manage.py shell
```
```python
from django.core.mail import send_mail
send_mail('测试', '测试邮件', '1480647675@qq.com', ['test@example.com'])
```

#### 3. 定时任务测试
在管理后台的"定时任务"中查看和管理Celery任务。

### 🔧 常见问题

#### 1. 权限问题
```bash
sudo chown -R weatherapp:weatherapp /home/weatherapp/projects/weatherblog/
sudo chmod -R 755 /home/weatherapp/projects/weatherblog/
```

#### 2. 静态文件问题
```bash
python manage.py collectstatic --noinput
```

#### 3. 数据库连接问题
```bash
# 使用测试脚本检查连接
python test_mysql_connection.py

# 检查 .env 文件中的数据库配置是否正确
cat .env | grep DB_
```

#### 4. PyMySQL相关问题
```bash
# 如果遇到PyMySQL相关错误，重新安装
pip uninstall PyMySQL
pip install PyMySQL==1.1.0

# 检查PyMySQL是否正确配置
python -c "import pymysql; pymysql.install_as_MySQLdb(); print('PyMySQL配置成功')"
```

#### 5. Redis连接问题
```bash
redis-cli ping
```

### 📈 性能优化

#### 1. 数据库优化
```sql
-- 添加索引
ALTER TABLE subscriptions_subscription ADD INDEX idx_user_city (user_id, city_id);
ALTER TABLE subscriptions_emaillog ADD INDEX idx_created_at (created_at);
```

#### 2. 缓存配置
在生产环境中可以考虑添加Redis缓存配置。

#### 3. 静态文件CDN
可以将静态文件部署到CDN以提高访问速度。

### 📞 技术支持

如果在部署过程中遇到问题：

1. 查看详细的部署文档：`DEPLOYMENT.md`
2. 检查系统日志：`sudo journalctl -f`
3. 检查应用日志：`tail -f logs/*.log`
4. 检查服务状态：`sudo supervisorctl status`

### 🎉 部署完成

部署成功后，您将拥有：

- ✅ 功能完整的天气订阅系统
- ✅ 美观的SimpleUI管理后台
- ✅ 自动化的邮件发送功能
- ✅ 定时任务调度系统
- ✅ 完整的日志记录
- ✅ 高可用的服务架构

祝您使用愉快！🌤️
