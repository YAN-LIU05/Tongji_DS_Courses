"""
权限控制
定义项目级别的权限类
"""
from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    对象级别权限
    只有创建者可以编辑，其他人只读
    """
    def has_object_permission(self, request, view, obj):
        # 读取权限对所有人开放
        if request.method in permissions.SAFE_METHODS:
            return True

        # 写入权限只给创建者
        return obj.created_by == request.user


class IsAdminOrReadOnly(BasePermission):
    """
    只有管理员可以写入，其他人只读
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsActiveUser(BasePermission):
    """
    只有激活的用户才能访问
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active


class IsSuperUserOrReadOnly(BasePermission):
    """
    只有超级管理员可以写入
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser


class HasAPIKey(BasePermission):
    """
    检查请求头中的API密钥
    """
    def has_permission(self, request, view):
        from django.conf import settings
        
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return False
        
        # 从配置中获取有效的API密钥列表
        valid_keys = getattr(settings, 'VALID_API_KEYS', [])
        return api_key in valid_keys


class ResourcePermission(BasePermission):
    """
    资源权限
    根据用户角色动态判断权限
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # GET, HEAD, OPTIONS 请求对认证用户开放
        if request.method in permissions.SAFE_METHODS:
            return True

        # POST 需要相应的添加权限
        if request.method == 'POST':
            return request.user.has_perm('add')

        # PUT, PATCH 需要更改权限
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('change')

        # DELETE 需要删除权限
        if request.method == 'DELETE':
            return request.user.has_perm('delete')

        return False

    def has_object_permission(self, request, view, obj):
        # 读取权限对所有认证用户开放
        if request.method in permissions.SAFE_METHODS:
            return True

        # 管理员拥有所有权限
        if request.user.is_staff:
            return True

        # 创建者可以编辑自己的对象
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user

        return False


class IsPublicOrAuthenticated(BasePermission):
    """
    公开资源允许匿名访问，私有资源需要认证
    """
    def has_object_permission(self, request, view, obj):
        # 如果对象有is_public属性且为True，允许访问
        if hasattr(obj, 'is_public') and obj.is_public:
            return True
        
        # 否则需要认证
        return request.user and request.user.is_authenticated


class RateLimitPermission(BasePermission):
    """
    简单的频率限制
    可以配合Django的缓存系统使用
    """
    def has_permission(self, request, view):
        from django.core.cache import cache
        from django.conf import settings
        
        # 获取用户IP
        ip = self.get_client_ip(request)
        
        # 构建缓存键
        cache_key = f'rate_limit:{ip}:{view.__class__.__name__}'
        
        # 获取当前请求次数
        requests_count = cache.get(cache_key, 0)
        
        # 获取限制配置（默认每分钟60次）
        limit = getattr(settings, 'API_RATE_LIMIT', 60)
        
        if requests_count >= limit:
            return False
        
        # 增加计数并设置过期时间（1分钟）
        cache.set(cache_key, requests_count + 1, 60)
        return True
    
    @staticmethod
    def get_client_ip(request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip