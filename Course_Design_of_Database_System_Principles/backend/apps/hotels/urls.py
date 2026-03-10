from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HoteldetailsViewSet

router = DefaultRouter()
router.register(r'hotels', HoteldetailsViewSet, basename='hotels')

urlpatterns = [
    path('', include(router.urls)),
]