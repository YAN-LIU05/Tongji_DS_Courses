#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.
文旅资源管理系统 - 主入口文件
"""
import os
import sys


def main():
    """Run administrative tasks."""
    # 设置默认的Django settings模块
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # 打印启动信息
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        print_startup_banner()
    
    execute_from_command_line(sys.argv)


def print_startup_banner():
    """打印启动横幅信息"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║          🏛️  文旅资源管理系统 Tourism Management System       ║
    ║                                                              ║
    ║          Version: 1.0.0                                      ║
    ║          Framework: Django 4.2 + DRF                         ║
    ║          Environment: {env}                            ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    📦 核心功能模块:
       ├─ 📍 文旅资源全景管理 (Resources)
       ├─ 🔗 旅游企业与运营关联 (Associations)  
       ├─ 📊 动态运行监测分析 (Monitoring)
       ├─ ☁️  精准气象服务 (Weather)
       └─ ⚠️  应急预警与风险管控 (Alerts)
    
    🌐 访问地址:
       ├─ 管理后台: http://127.0.0.1:8000/admin/
       ├─ API文档:  http://127.0.0.1:8000/swagger/
       ├─ ReDoc:    http://127.0.0.1:8000/redoc/
       └─ API Root: http://127.0.0.1:8000/api/v1/
    
    🚀 系统启动中...
    """
    
    env = os.environ.get('DJANGO_ENV', 'development').upper()
    print(banner.format(env=env))


if __name__ == '__main__':
    main()