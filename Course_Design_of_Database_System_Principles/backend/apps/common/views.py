"""
公共视图
提供通用的视图类和方法
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from .models import Config
from .serializers import ConfigSerializer
import logging

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """
    健康检查视图
    用于监控系统状态
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """健康检查"""
        from django.db import connection
        
        health_status = {
            'status': 'healthy',
            'database': 'unknown',
            'cache': 'unknown'
        }

        # 检查数据库连接
        try:
            connection.ensure_connection()
            health_status['database'] = 'connected'
        except Exception as e:
            health_status['database'] = f'error: {str(e)}'
            health_status['status'] = 'unhealthy'

        # 检查缓存
        try:
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') == 'ok':
                health_status['cache'] = 'working'
            else:
                health_status['cache'] = 'not working'
                health_status['status'] = 'unhealthy'
        except Exception as e:
            health_status['cache'] = f'error: {str(e)}'
            health_status['status'] = 'unhealthy'

        status_code = status.HTTP_200_OK if health_status['status'] == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return Response(health_status, status=status_code)


class ConfigViewSet(viewsets.ModelViewSet):
    """
    系统配置视图集
    """
    queryset = Config.objects.filter(is_deleted=False)
    serializer_class = ConfigSerializer
    filterset_fields = ['category', 'is_public']
    search_fields = ['key', 'description']
    ordering_fields = ['created_at', 'category']

    @action(detail=False, methods=['get'])
    def public(self, request):
        """获取所有公开配置"""
        configs = self.queryset.filter(is_public=True)
        serializer = self.get_serializer(configs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """按分类获取配置"""
        category = request.query_params.get('category')
        if not category:
            return Response({'error': '缺少category参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        configs = self.queryset.filter(category=category)
        serializer = self.get_serializer(configs, many=True)
        return Response(serializer.data)


class BaseViewSet(viewsets.ModelViewSet):
    """
    基础视图集
    提供通用的CRUD操作和额外功能
    """
    def perform_create(self, serializer):
        """创建时自动记录创建者"""
        if hasattr(serializer.Meta.model, 'created_by'):
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()

    def perform_update(self, serializer):
        """更新时自动记录更新者"""
        if hasattr(serializer.Meta.model, 'updated_by'):
            serializer.save(updated_by=self.request.user)
        else:
            serializer.save()

    def perform_destroy(self, instance):
        """删除（软删除）"""
        if hasattr(instance, 'is_deleted'):
            instance.delete()  # 会触发软删除
        else:
            instance.delete()  # 硬删除

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """恢复已删除的记录"""
        instance = self.get_object()
        if hasattr(instance, 'restore'):
            instance.restore()
            return Response({'message': '恢复成功'})
        return Response({'error': '不支持恢复操作'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """批量删除"""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': '请提供要删除的ID列表'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(id__in=ids)
        count = queryset.count()
        
        for instance in queryset:
            self.perform_destroy(instance)
        
        return Response({'message': f'成功删除{count}条记录'})