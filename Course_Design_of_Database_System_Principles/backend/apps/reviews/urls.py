"""
Reviews (Weather) URLs
天气模块路由配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LocationweatherViewSet,
    WeatheralertViewSet,
    AlertaffectedpoiViewSet,
    WeatherforecastViewSet,
)

app_name = 'reviews'

# 创建路由器
router = DefaultRouter()

# 注册视图集
router.register(r'locations', LocationweatherViewSet, basename='location-weather')
router.register(r'alerts', WeatheralertViewSet, basename='weather-alert')
router.register(r'alert-affected-pois', AlertaffectedpoiViewSet, basename='alert-affected-poi')
router.register(r'forecasts', WeatherforecastViewSet, basename='weather-forecast')

urlpatterns = [
    # 路由器生成的URL
    path('', include(router.urls)),
]