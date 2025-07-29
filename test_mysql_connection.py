#!/usr/bin/env python3
"""
测试PyMySQL数据库连接脚本
使用方法: python test_mysql_connection.py
"""

import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pymysql_import():
    """测试PyMySQL导入"""
    try:
        import pymysql
        print("✅ PyMySQL导入成功")
        print(f"   版本: {pymysql.__version__}")
        return True
    except ImportError as e:
        print(f"❌ PyMySQL导入失败: {e}")
        print("   请运行: pip install PyMySQL")
        return False

def test_mysql_connection():
    """测试MySQL数据库连接"""
    try:
        import pymysql
        
        # 配置PyMySQL作为MySQLdb的替代
        pymysql.install_as_MySQLdb()
        
        # 测试连接参数 (请根据实际情况修改)
        connection_params = {
            'host': 'localhost',
            'user': 'root',  # 或者您的MySQL用户名
            'password': 'hubing123',  # 请修改为您的MySQL密码
            'charset': 'utf8mb4',
            'port': 3306
        }
        
        print("🔍 测试MySQL连接...")
        print(f"   主机: {connection_params['host']}")
        print(f"   端口: {connection_params['port']}")
        print(f"   用户: {connection_params['user']}")
        
        # 尝试连接
        connection = pymysql.connect(**connection_params)
        
        with connection.cursor() as cursor:
            # 执行简单查询
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✅ MySQL连接成功")
            print(f"   MySQL版本: {version[0]}")
            
            # 检查是否存在weatherblog数据库
            cursor.execute("SHOW DATABASES LIKE 'weatherblog'")
            db_exists = cursor.fetchone()
            
            if db_exists:
                print("✅ weatherblog数据库已存在")
            else:
                print("⚠️  weatherblog数据库不存在")
                print("   请创建数据库: CREATE DATABASE weatherblog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ MySQL连接失败: {e}")
        print("\n🔧 可能的解决方案:")
        print("   1. 检查MySQL服务是否运行: sudo systemctl status mysql")
        print("   2. 检查连接参数是否正确")
        print("   3. 检查MySQL用户权限")
        print("   4. 检查防火墙设置")
        return False

def test_django_settings():
    """测试Django设置"""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weatherblog.settings')
        
        import django
        from django.conf import settings
        
        django.setup()
        
        print("🔍 测试Django配置...")
        
        # 测试数据库配置
        db_config = settings.DATABASES['default']
        print(f"   数据库引擎: {db_config['ENGINE']}")
        print(f"   数据库名称: {db_config['NAME']}")
        print(f"   数据库主机: {db_config['HOST']}")
        print(f"   数据库端口: {db_config['PORT']}")
        
        # 测试数据库连接
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] == 1:
                print("✅ Django数据库连接成功")
                return True
        
    except Exception as e:
        print(f"❌ Django配置测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("🧪 PyMySQL + Django 连接测试")
    print("=" * 50)
    
    success_count = 0
    total_tests = 3
    
    # 测试1: PyMySQL导入
    if test_pymysql_import():
        success_count += 1
    
    print()
    
    # 测试2: MySQL连接
    if test_mysql_connection():
        success_count += 1
    
    print()
    
    # 测试3: Django设置
    if test_django_settings():
        success_count += 1
    
    print()
    print("=" * 50)
    print(f"📊 测试结果: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！PyMySQL配置正确")
        print("\n📝 下一步:")
        print("   1. 运行数据库迁移: python manage.py migrate")
        print("   2. 创建超级用户: python manage.py createsuperuser")
        print("   3. 启动开发服务器: python manage.py runserver")
    else:
        print("⚠️  部分测试失败，请检查配置")
        
    print("=" * 50)

if __name__ == "__main__":
    main()
