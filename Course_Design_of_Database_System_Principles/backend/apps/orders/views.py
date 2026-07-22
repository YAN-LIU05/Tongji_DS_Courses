"""
订单模块视图
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q

from .models import Enterpriseinfo, Enterprisepoilink
from .serializers import (
    EnterpriseinfoSerializer,
    EnterpriseinfoListSerializer,
    EnterpriseinfoCreateSerializer,
    EnterpriseinfoUpdateSerializer,
    EnterprisepoilinkSerializer,
    EnterprisepoilinkCreateSerializer,
    EnterprisepoilinkListSerializer,
)


class EnterpriseinfoViewSet(viewsets.ModelViewSet):
    """
    企业信息视图集
    
    list: 获取企业列表
    retrieve: 获取企业详情
    create: 创建企业
    update: 更新企业
    partial_update: 部分更新企业
    destroy: 删除企业
    """
    queryset = Enterpriseinfo.objects.prefetch_related(
        'enterprisepoilink_set__poi'
    ).all()
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['enterprise_type']
    search_fields = ['enterprise_name', 'enterprise_type']
    ordering_fields = ['enterprise_id', 'enterprise_name']
    ordering = ['enterprise_id']
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'list':
            return EnterpriseinfoListSerializer
        elif self.action == 'create':
            return EnterpriseinfoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EnterpriseinfoUpdateSerializer
        return EnterpriseinfoSerializer
    
    @action(detail=True, methods=['get'])
    def poi_links(self, request, pk=None):
        """
        获取企业关联的所有POI
        """
        enterprise = self.get_object()
        links = enterprise.enterprisepoilink_set.select_related('poi').all()
        
        serializer = EnterprisepoilinkSerializer(links, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_poi(self, request, pk=None):
        """
        为企业添加POI关联
        
        参数：
        - poi: POI ID（必填）
        - relationship_type: 关系类型（可选）
        """
        enterprise = self.get_object()
        
        data = {
            'enterprise': enterprise.enterprise_id,
            'poi': request.data.get('poi'),
            'relationship_type': request.data.get('relationship_type')
        }
        
        serializer = EnterprisepoilinkCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        link = serializer.save()
        
        return Response({
            'message': 'POI关联添加成功',
            'link': EnterprisepoilinkSerializer(link).data
        })
    
    @action(detail=True, methods=['delete'])
    def remove_poi(self, request, pk=None):
        """
        移除企业的POI关联
        
        参数：
        - poi: POI ID（必填）
        """
        enterprise = self.get_object()
        poi_id = request.query_params.get('poi')
        
        if not poi_id:
            return Response(
                {'error': '请提供POI ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            link = Enterprisepoilink.objects.get(
                enterprise=enterprise,
                poi_id=poi_id
            )
            link.delete()
            return Response({'message': 'POI关联已移除'})
        except Enterprisepoilink.DoesNotExist:
            return Response(
                {'error': '该POI关联不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        企业统计信息
        
        返回：
        - total_enterprises: 企业总数
        - by_type: 按类型分组统计
        - top_enterprises: POI数量最多的企业
        """
        total_enterprises = self.queryset.count()
        
        # 按类型统计
        by_type = self.queryset.values('enterprise_type').annotate(
            count=Count('enterprise_id')
        ).order_by('-count')
        
        # POI数量最多的企业（Top 10）
        top_enterprises = self.queryset.annotate(
            poi_count=Count('enterprisepoilink')
        ).order_by('-poi_count')[:10]
        
        top_enterprises_data = [
            {
                'enterprise_id': e.enterprise_id,
                'enterprise_name': e.enterprise_name,
                'enterprise_type': e.enterprise_type,
                'poi_count': e.poi_count
            }
            for e in top_enterprises
        ]
        
        return Response({
            'total_enterprises': total_enterprises,
            'by_type': list(by_type),
            'top_enterprises': top_enterprises_data
        })
    
    @action(detail=False, methods=['get'])
    def search_by_poi(self, request):
        """
        根据POI搜索企业
        
        参数：
        - poi_name: POI名称（模糊搜索）
        - poi_id: POI ID（精确搜索）
        """
        poi_name = request.query_params.get('poi_name')
        poi_id = request.query_params.get('poi_id')
        
        queryset = self.queryset
        
        if poi_id:
            queryset = queryset.filter(enterprisepoilink__poi_id=poi_id).distinct()
        elif poi_name:
            queryset = queryset.filter(
                enterprisepoilink__poi__poi_name__icontains=poi_name
            ).distinct()
        else:
            return Response(
                {'error': '请提供 poi_name 或 poi_id 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EnterpriseinfoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EnterpriseinfoListSerializer(queryset, many=True)
        return Response(serializer.data)


class EnterprisepoilinkViewSet(viewsets.ModelViewSet):
    """
    企业POI关联视图集
    
    list: 获取关联列表
    retrieve: 获取关联详情
    create: 创建关联
    update: 更新关联
    partial_update: 部分更新关联
    destroy: 删除关联
    """
    queryset = Enterprisepoilink.objects.select_related(
        'enterprise',
        'poi'
    ).all()
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['enterprise', 'poi', 'relationship_type']
    search_fields = ['enterprise__enterprise_name', 'poi__poi_name', 'relationship_type']
    ordering_fields = ['e_id']
    ordering = ['e_id']
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'list':
            return EnterprisepoilinkListSerializer
        elif self.action == 'create':
            return EnterprisepoilinkCreateSerializer
        return EnterprisepoilinkSerializer
    
    @action(detail=False, methods=['get'])
    def by_enterprise(self, request):
        """
        按企业ID获取所有POI关联
        
        参数：
        - enterprise_id: 企业ID（必填）
        """
        enterprise_id = request.query_params.get('enterprise_id')
        
        if not enterprise_id:
            return Response(
                {'error': '请提供 enterprise_id 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(enterprise_id=enterprise_id)
        
        serializer = EnterprisepoilinkListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_poi(self, request):
        """
        按POI ID获取所有企业关联
        
        参数：
        - poi_id: POI ID（必填）
        """
        poi_id = request.query_params.get('poi_id')
        
        if not poi_id:
            return Response(
                {'error': '请提供 poi_id 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(poi_id=poi_id)
        
        serializer = EnterprisepoilinkListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_relationship(self, request):
        """
        按关系类型筛选
        
        参数：
        - relationship_type: 关系类型（必填）
        """
        relationship_type = request.query_params.get('relationship_type')
        
        if not relationship_type:
            return Response(
                {'error': '请提供 relationship_type 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(relationship_type__icontains=relationship_type)
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EnterprisepoilinkListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EnterprisepoilinkListSerializer(queryset, many=True)
        return Response(serializer.data)