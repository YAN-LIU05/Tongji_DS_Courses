from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'users'

# 如果你有 UserViewSet（用于用户 CRUD 操作），就用 router
# router = DefaultRouter()
# router.register(r'list', views.UserViewSet, basename='user-list')

urlpatterns = [
    # 认证相关接口
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # 如果有 router，取消注释下面这行
    # path('', include(router.urls)),
]