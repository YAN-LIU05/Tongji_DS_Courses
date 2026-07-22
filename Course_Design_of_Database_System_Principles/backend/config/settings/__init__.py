"""
Django 设置初始化
根据环境变量自动加载对应的配置文件
"""
import os

# 获取环境变量（注意：这里的 env 变量是字符串，不是函数）
django_env = os.environ.get('DJANGO_ENV', 'development').lower()

# 根据环境加载不同配置
if django_env == 'production':
    from .prod import *
    print(f"🚀 当前运行环境: {django_env.upper()}")
else:
    # 默认使用开发环境配置
    from .dev import *
    print(f"✅ 当前运行环境: {django_env.upper()}")