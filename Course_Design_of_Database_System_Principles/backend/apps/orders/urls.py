"""
Orders URLs
订单模块路由配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EnterpriseinfoViewSet,
    EnterprisepoilinkViewSet,
)

app_name = 'orders'

# 创建路由器
router = DefaultRouter()

# 注册视图集
router.register(r'enterprises', EnterpriseinfoViewSet, basename='enterprise')
router.register(r'enterprise-poi-links', EnterprisepoilinkViewSet, basename='enterprise-poi-link')

urlpatterns = [
    # 路由器生成的URL
    path('', include(router.urls)),
]