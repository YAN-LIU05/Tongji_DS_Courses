"""
生产环境配置
"""
from .base import *

# ==========================================
# 生产环境配置
# ==========================================

DEBUG = False

# 必须设置允许的主机
ALLOWED_HOSTS = env('ALLOWED_HOSTS', default='').split(',')

# ==========================================
# 数据库配置（生产环境使用MySQL）
# ==========================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'CONN_MAX_AGE': 600,
    }
}

# ==========================================
# 缓存配置（生产环境使用Redis）
# ==========================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{env('REDIS_HOST')}:{env('REDIS_PORT')}/{env('REDIS_DB', default='0')}",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50}
        }
    }
}

# ==========================================
# 安全配置
# ==========================================

# HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 其他安全设置
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# ==========================================
# 静态文件（使用 WhiteNoise 或 CDN）
# ==========================================

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# ==========================================
# 日志配置
# ==========================================

LOGGING['handlers']['file'] = {
    'level': 'ERROR',
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': BASE_DIR / 'logs' / 'django.log',
    'maxBytes': 1024 * 1024 * 10,  # 10MB
    'backupCount': 10,
    'formatter': 'verbose',
}

LOGGING['root']['handlers'].append('file')
LOGGING['root']['level'] = 'WARNING'

print("🚀 生产环境配置加载完成")