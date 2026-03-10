# apps/users/permissions.py

from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    只允许对象的所有者或管理员进行操作
    """
    
    def has_object_permission(self, request, view, obj):
        # 管理员拥有所有权限
        if request.user and request.user.is_staff:
            return True
        
        # 对象所有者拥有权限
        return obj == request.user


class IsOwner(permissions.BasePermission):
    """
    只允许对象的所有者进行操作
    """
    
    def has_object_permission(self, request, view, obj):
        return obj == request.user