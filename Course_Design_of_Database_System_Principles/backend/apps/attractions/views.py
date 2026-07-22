"""
景点模块视图
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from .models import Poimaster, Dynamicdata, Scenicspotdetails
from .serializers import (
    PoimasterSerializer,
    PoimasterListSerializer,
    DynamicdataSerializer,
    ScenicspotdetailsSerializer,
    ScenicspotdetailsCreateSerializer
)


class PoimasterViewSet(viewsets.ModelViewSet):
    """
    POI 主表视图集
    
    list: 获取 POI 列表
    retrieve: 获取单个 POI 详情
    create: 创建 POI
    update: 更新 POI
    partial_update: 部分更新 POI
    destroy: 删除 POI
    """
    queryset = Poimaster.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['poi_type']
    search_fields = ['poi_name', 'address', 'description']
    ordering_fields = ['poi_id', 'poi_name']
    ordering = ['poi_id']
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'list':
            return PoimasterListSerializer
        return PoimasterSerializer
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        搜索 POI
        
        参数：
        - q: 搜索关键词
        - poi_type: POI 类型
        """
        queryset = self.get_queryset()
        
        # 关键词搜索
        q = request.query_params.get('q', '')
        if q:
            queryset = queryset.filter(
                Q(poi_name__icontains=q) |
                Q(address__icontains=q) |
                Q(description__icontains=q)
            )
        
        # 类型筛选
        poi_type = request.query_params.get('poi_type')
        if poi_type:
            queryset = queryset.filter(poi_type=poi_type)
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """获取所有 POI 类型"""
        types = Poimaster.objects.values_list('poi_type', flat=True).distinct()
        return Response(list(types))
    
    @action(detail=True, methods=['get'])
    def nearby(self, request, pk=None):
        """
        获取附近的 POI
        
        参数：
        - radius: 半径（公里），默认 5
        """
        poi = self.get_object()
        
        if not poi.latitude or not poi.longitude:
            return Response(
                {'error': '该 POI 没有坐标信息'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        radius = float(request.query_params.get('radius', 5))
        
        # 简单的经纬度范围计算（1度约等于111公里）
        lat_range = radius / 111.0
        lng_range = radius / (111.0 * float(poi.latitude))
        
        nearby_pois = Poimaster.objects.filter(
            latitude__range=(float(poi.latitude) - lat_range, float(poi.latitude) + lat_range),
            longitude__range=(float(poi.longitude) - lng_range, float(poi.longitude) + lng_range)
        ).exclude(poi_id=poi.poi_id)[:20]
        
        serializer = PoimasterListSerializer(nearby_pois, many=True)
        return Response(serializer.data)


class DynamicdataViewSet(viewsets.ModelViewSet):
    """
    动态数据视图集
    """
    queryset = Dynamicdata.objects.all()
    serializer_class = DynamicdataSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['poi']
    ordering = ['-record_time']

    def perform_create(self, serializer):
        """
        创建动态数据时，统一使用 timezone.now()
        彻底解决 8 小时时差问题
        """
        serializer.save(record_time=timezone.now())
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """获取最新的动态数据"""
        poi_id = request.query_params.get('poi_id')
        
        if not poi_id:
            return Response(
                {'error': '缺少 poi_id 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        latest_data = Dynamicdata.objects.filter(poi_id=poi_id).order_by('-record_time').first()
        
        if not latest_data:
            return Response(
                {'error': '未找到数据'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(latest_data)
        return Response(serializer.data)


class ScenicspotdetailsViewSet(viewsets.ModelViewSet):
    """
    景点详情视图集
    """
    queryset = Scenicspotdetails.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['scenic_spot', 'level']
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action in ['create', 'update', 'partial_update']:
            return ScenicspotdetailsCreateSerializer
        return ScenicspotdetailsSerializer
    
    @action(detail=False, methods=['get'])
    def by_poi(self, request):
        """根据 POI ID 获取详情"""
        poi_id = request.query_params.get('poi_id')
        
        if not poi_id:
            return Response(
                {'error': '缺少 poi_id 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        details = self.queryset.filter(scenic_spot_id=poi_id).first()
        
        if not details:
            return Response(
                {'error': '未找到景点详情'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(details)
        return Response(serializer.data)