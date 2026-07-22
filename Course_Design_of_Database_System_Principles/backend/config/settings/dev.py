"""
开发环境配置
"""
from .base import *

# ==========================================
# 开发环境特定配置
# ==========================================

DEBUG = True

# ==========================================
# 数据库配置 - 支持SQLite和MySQL
# ==========================================

DB_ENGINE = env('DB_ENGINE', default='django.db.backends.sqlite3')

if DB_ENGINE == 'django.db.backends.sqlite3':
    # 使用SQLite（适合快速测试）
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("📦 使用SQLite数据库")
else:
    # 使用MySQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': env('DB_NAME', default='tourism_db'),
            'USER': env('DB_USER', default='root'),
            'PASSWORD': env('DB_PASSWORD', default=''),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            }
        }
    }
    print("🐬 使用MySQL数据库")

# ==========================================
# 缓存配置
# ==========================================

REDIS_ENABLED = env('REDIS_ENABLED', default='False', cast_type=bool)

if REDIS_ENABLED:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f"redis://{env('REDIS_HOST', default='localhost')}:{env('REDIS_PORT', default='6379')}/{env('REDIS_DB', default='0')}",
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
    print("🔴 使用Redis缓存")
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }
    print("💾 使用内存缓存")

# ==========================================
# Celery 配置（开发环境同步执行）
# ==========================================

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ==========================================
# 开发工具
# ==========================================

# Django Extensions（如果已安装）
try:
    import django_extensions
    INSTALLED_APPS += ['django_extensions']
    print("🔧 Django Extensions 已启用")
except ImportError:
    pass

# ==========================================
# 安全配置（开发环境放宽）
# ==========================================

ALLOWED_HOSTS = ['*']

# CORS 配置
CORS_ALLOW_ALL_ORIGINS = True

# ==========================================
# 静态文件配置
# ==========================================

STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'

# ==========================================
# 日志级别
# ==========================================

LOGGING['root']['level'] = 'DEBUG'

print("🔧 开发环境配置加载完成")