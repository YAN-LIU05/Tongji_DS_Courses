"""
景点模块路由
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PoimasterViewSet, DynamicdataViewSet, ScenicspotdetailsViewSet

router = DefaultRouter()
router.register('pois', PoimasterViewSet, basename='poi')
router.register('dynamic', DynamicdataViewSet, basename='dynamic')
router.register('details', ScenicspotdetailsViewSet, basename='detail')


urlpatterns = [
    path('', include(router.urls)),
]