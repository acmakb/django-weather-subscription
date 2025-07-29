# 配置PyMySQL作为MySQLdb的替代
import pymysql
pymysql.install_as_MySQLdb()

# 确保Celery在Django启动时被加载
from .celery import app as celery_app

__all__ = ('celery_app',)