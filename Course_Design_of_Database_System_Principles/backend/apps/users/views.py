from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny


class UserLoginView(APIView):
    """用户登录"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'code': 400,
                'message': '用户名和密码不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证用户
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response({
                'code': 401,
                'message': '用户名或密码错误'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 生成或获取 token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'code': 200,
            'message': '登录成功',
            'data': {
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff
            }
        })


class UserRegisterView(APIView):
    """用户注册"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        
        if not all([username, password, email]):
            return Response({
                'code': 400,
                'message': '用户名、密码和邮箱不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查用户是否已存在
        if User.objects.filter(username=username).exists():
            return Response({
                'code': 400,
                'message': '用户名已存在'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({
                'code': 400,
                'message': '邮箱已被注册'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建用户
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        
        return Response({
            'code': 200,
            'message': '注册成功',
            'data': {
                'username': user.username,
                'email': user.email
            }
        })


class UserProfileView(APIView):
    """获取用户信息"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff,
                'date_joined': user.date_joined
            }
        })


class UserLogoutView(APIView):
    """用户登出"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # 删除 token
        request.user.auth_token.delete()
        return Response({
            'code': 200,
            'message': '登出成功'
        })