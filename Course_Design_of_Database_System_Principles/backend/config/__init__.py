"""
文旅资源管理系统配置包
Tourism Resource Management System Configuration Package
"""

# 确保使用正确的设置模块
from .celery import app as celery_app

__all__ = ('celery_app',)