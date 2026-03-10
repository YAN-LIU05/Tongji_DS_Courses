# apps/users/serializers.py

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'avatar',
            'first_name', 'last_name', 'is_active', 'is_staff',
            'is_superuser', 'date_joined', 'last_login',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'created_at',
            'updated_at', 'is_superuser'
        ]


class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'phone']
        extra_kwargs = {
            'email': {'required': True},
        }
    
    def validate(self, attrs):
        """验证密码是否一致"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': '两次输入的密码不一致'
            })
        return attrs
    
    def validate_username(self, value):
        """验证用户名"""
        if len(value) < 3:
            raise serializers.ValidationError('用户名至少需要3个字符')
        if len(value) > 20:
            raise serializers.ValidationError('用户名不能超过20个字符')
        return value
    
    def validate_phone(self, value):
        """验证手机号"""
        if value:
            if len(value) != 11:
                raise serializers.ValidationError('手机号必须是11位数字')
            if not value.isdigit():
                raise serializers.ValidationError('手机号只能包含数字')
            if User.objects.filter(phone=value).exists():
                raise serializers.ValidationError('该手机号已被注册')
        return value
    
    def create(self, validated_data):
        """创建用户"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """验证登录信息"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        # 支持用户名、邮箱、手机号登录
        user = None
        
        # 尝试通过用户名登录
        if User.objects.filter(username=username).exists():
            user = authenticate(username=username, password=password)
        # 尝试通过邮箱登录
        elif User.objects.filter(email=username).exists():
            user_obj = User.objects.get(email=username)
            user = authenticate(username=user_obj.username, password=password)
        # 尝试通过手机号登录
        elif User.objects.filter(phone=username).exists():
            user_obj = User.objects.get(phone=username)
            user = authenticate(username=user_obj.username, password=password)
        
        if not user:
            raise serializers.ValidationError('用户名或密码错误')
        
        if not user.is_active:
            raise serializers.ValidationError('该账号已被禁用')
        
        attrs['user'] = user
        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户信息更新序列化器"""
    
    class Meta:
        model = User
        fields = ['email', 'phone', 'first_name', 'last_name']
    
    def validate_email(self, value):
        """验证邮箱"""
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError('该邮箱已被使用')
        return value
    
    def validate_phone(self, value):
        """验证手机号"""
        if value:
            user = self.context['request'].user
            if User.objects.exclude(pk=user.pk).filter(phone=value).exists():
                raise serializers.ValidationError('该手机号已被使用')
            if len(value) != 11 or not value.isdigit():
                raise serializers.ValidationError('手机号格式不正确')
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""
    
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """验证原密码"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码不正确')
        return value
    
    def validate(self, attrs):
        """验证新密码"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': '两次输入的新密码不一致'
            })
        return attrs
    
    def save(self, **kwargs):
        """保存新密码"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class AvatarUploadSerializer(serializers.ModelSerializer):
    """头像上传序列化器"""
    
    class Meta:
        model = User
        fields = ['avatar']
    
    def validate_avatar(self, value):
        """验证头像文件"""
        # 验证文件大小（最大5MB）
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('头像文件大小不能超过5MB')
        
        # 验证文件格式
        allowed_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if value.content_type not in allowed_formats:
            raise serializers.ValidationError(
                '不支持的图片格式，请上传 JPG、PNG、GIF 或 WEBP 格式的图片'
            )
        
        return value


class UserListSerializer(serializers.ModelSerializer):
    """用户列表序列化器（管理员用）"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'avatar',
            'first_name', 'last_name', 'is_active', 'is_staff',
            'is_superuser', 'date_joined', 'last_login',
            'created_at', 'updated_at'
        ]


class UserAdminUpdateSerializer(serializers.ModelSerializer):
    """管理员更新用户序列化器"""
    
    class Meta:
        model = User
        fields = ['is_active', 'is_staff', 'email', 'phone', 'first_name', 'last_name']