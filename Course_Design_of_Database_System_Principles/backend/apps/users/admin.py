# apps/users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理后台"""
    
    list_display = [
        'id', 'username', 'email', 'phone', 'avatar_display',
        'is_active', 'is_staff', 'date_joined', 'last_login'
    ]
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'phone', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'password')
        }),
        ('个人信息', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')
        }),
        ('权限', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('重要日期', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login', 'created_at', 'updated_at']
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2'),
        }),
    )
    
    def avatar_display(self, obj):
        """显示头像缩略图"""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%;" />',
                obj.avatar.url
            )
        return '-'
    avatar_display.short_description = '头像'