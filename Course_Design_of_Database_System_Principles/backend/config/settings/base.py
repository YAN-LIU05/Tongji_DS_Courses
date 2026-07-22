"""
Django 基础配置
适用于所有环境的通用配置
"""
from pathlib import Path
import os
import sys

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ============= 环境变量读取函数 =============
def get_env(key, default=None, cast_type=str):
    """
    从环境变量读取配置
    
    Args:
        key: 环境变量键名
        default: 默认值
        cast_type: 类型转换函数（str, int, bool等）
    
    Returns:
        转换后的环境变量值或默认值
    """
    value = os.environ.get(key)
    
    # 如果环境变量不存在，返回默认值
    if value is None:
        return default
    
    # 布尔类型特殊处理
    if cast_type == bool:
        if isinstance(value, bool):
            return value
        return str(value).lower() in ('true', '1', 'yes', 'on')
    
    # 整数类型
    if cast_type == int:
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    # 浮点数类型
    if cast_type == float:
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    # 字符串类型（默认）
    return str(value)

# 创建简短别名
env = get_env
# ==========================================

# 加载 .env 文件（如果存在）
env_file = BASE_DIR / '.env'
if env_file.exists():
    print(f"📄 加载环境变量文件: {env_file}")
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过注释和空行
            if not line or line.startswith('#'):
                continue
            # 解析 KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                # 移除引号
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                # 设置环境变量
                os.environ.setdefault(key, value)
else:
    print(f"⚠️ 未找到 .env 文件: {env_file}")

# ==========================================
# 核心配置
# ==========================================

# 安全密钥
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-this-in-production')

# 调试模式
DEBUG = env('DEBUG', default=False, cast_type=bool)

# 允许的主机
allowed_hosts_str = env('ALLOWED_HOSTS', default='localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',')]

# 应用定义
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 第三方应用
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'drf_yasg',
    'django_filters',
    
    # 本地应用
    'apps.users',
    'apps.attractions',
    'apps.hotels',
    'apps.reviews',
    'apps.orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ==========================================
# 数据库配置（在各环境配置中覆盖）
# ==========================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ==========================================
# 密码验证
# ==========================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==========================================
# 国际化
# ==========================================

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ==========================================
# 静态文件和媒体文件
# ==========================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==========================================
# 默认主键字段类型
# ==========================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================
# 自定义用户模型
# ==========================================

AUTH_USER_MODEL = 'users.User'

# Swagger 配置
SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': True,
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        },
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
}

# ==========================================
# REST Framework 配置
# ==========================================

# ==================== REST Framework 配置 ====================
REST_FRAMEWORK = {
    # 默认认证类
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    
    # 默认权限类
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    
    # 分页配置
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    
    # 过滤后端
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    
    # 渲染器
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    
    # 解析器
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    
    # 异常处理
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    
    # 时区
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
    'TIME_FORMAT': '%H:%M:%S',
}

# ==========================================
# CORS 配置
# ==========================================

CORS_ALLOW_ALL_ORIGINS = True  # 开发环境允许所有来源

# ==========================================
# Celery 配置
# ==========================================

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# ==========================================
# 日志配置
# ==========================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

print("✅ 基础配置加载完成")