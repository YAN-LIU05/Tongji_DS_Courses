"""
Common URLs - 认证和通用接口
"""
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from django.http import JsonResponse
from django.views.decorators.http import require_GET

app_name = 'common'


@require_GET
def health_check(request):
    """健康检查端点"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'tourism_database',
        'version': '1.0.0'
    })


@require_GET
def readiness_check(request):
    """就绪检查端点"""
    from django.db import connection
    
    try:
        # 检查数据库连接
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'ready',
            'database': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'not_ready',
            'error': str(e)
        }, status=503)


urlpatterns = [
    # ==================== JWT 认证 ====================
    # 登录获取 Token
    path('token/', TokenObtainPairView.as_view(), name='token_obtain'),
    # 刷新 Token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 验证 Token
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # ==================== 健康检查 ====================
    path('health/', health_check, name='health'),
    path('health/readiness/', readiness_check, name='readiness'),
]