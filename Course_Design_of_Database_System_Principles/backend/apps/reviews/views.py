"""
天气模块视图
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Avg, Max, Min
from django.utils import timezone
from datetime import timedelta

from .models import (
    Locationweather,
    Weatheralert,
    Alertaffectedpoi,
    Weatherforecast
)
from .serializers import (
    LocationweatherSerializer,
    LocationweatherListSerializer,
    LocationweatherCreateSerializer,
    LocationweatherUpdateSerializer,
    WeatheralertSerializer,
    WeatheralertListSerializer,
    WeatheralertCreateSerializer,
    WeatheralertUpdateSerializer,
    AlertaffectedpoiSerializer,
    AlertaffectedpoiCreateSerializer,
    AlertaffectedpoiListSerializer,
    WeatherforecastSerializer,
    WeatherforecastListSerializer,
    WeatherforecastCreateSerializer,
)


class LocationweatherViewSet(viewsets.ModelViewSet):
    """
    位置天气视图集
    
    list: 获取位置天气列表
    retrieve: 获取位置天气详情
    create: 创建位置天气
    update: 更新位置天气
    partial_update: 部分更新位置天气
    destroy: 删除位置天气
    """
    queryset = Locationweather.objects.select_related('poi').prefetch_related(
        'weatherforecast_set'
    ).all()
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['poi', 'conditions']
    search_fields = ['location_name', 'conditions']
    ordering_fields = ['location_id', 'update_time', 'temperature']
    ordering = ['-update_time']
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'list':
            return LocationweatherListSerializer
        elif self.action == 'create':
            return LocationweatherCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return LocationweatherUpdateSerializer
        return LocationweatherSerializer
    
    @action(detail=True, methods=['get'])
    def forecasts(self, request, pk=None):
        """
        获取位置的天气预报
        
        参数：
        - days: 预报天数（默认7天）
        """
        location = self.get_object()
        days = int(request.query_params.get('days', 7))
        
        forecasts = location.weatherforecast_set.all()[:days]
        serializer = WeatherforecastSerializer(forecasts, many=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_weather(self, request, pk=None):
        """
        更新位置天气信息
        
        参数：
        - temperature: 温度（必填）
        - conditions: 天气状况（必填）
        """
        location = self.get_object()
        
        temperature = request.data.get('temperature')
        conditions = request.data.get('conditions')
        
        if not temperature or not conditions:
            return Response(
                {'error': '请提供温度和天气状况'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        location.temperature = temperature
        location.conditions = conditions
        location.update_time = timezone.now()
        location.save()
        
        serializer = self.get_serializer(location)
        return Response({
            'message': '天气信息已更新',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_city(self, request):
        """
        按城市查询天气
        
        参数：
        - city: 城市名称（必填）
        """
        city = request.query_params.get('city')
        
        if not city:
            return Response(
                {'error': '请提供城市名称'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(poi__city_name__icontains=city)
        
        serializer = LocationweatherListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent_updates(self, request):
        """
        最近更新的天气信息
        
        参数：
        - hours: 最近多少小时（默认24小时）
        """
        hours = int(request.query_params.get('hours', 24))
        time_threshold = timezone.now() - timedelta(hours=hours)
        
        queryset = self.queryset.filter(
            update_time__gte=time_threshold
        ).order_by('-update_time')
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = LocationweatherListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = LocationweatherListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        天气统计信息
        
        返回：
        - total_locations: 位置总数
        - by_conditions: 按天气状况分组统计
        - temperature_stats: 温度统计
        """
        total_locations = self.queryset.count()
        
        # 按天气状况统计
        by_conditions = self.queryset.values('conditions').annotate(
            count=Count('location_id')
        ).order_by('-count')
        
        # 温度统计
        temp_stats = self.queryset.aggregate(
            avg_temp=Avg('temperature'),
            max_temp=Max('temperature'),
            min_temp=Min('temperature')
        )
        
        return Response({
            'total_locations': total_locations,
            'by_conditions': list(by_conditions),
            'temperature_stats': temp_stats
        })


class WeatheralertViewSet(viewsets.ModelViewSet):
    """
    天气预警视图集
    
    list: 获取天气预警列表
    retrieve: 获取天气预警详情
    create: 创建天气预警
    update: 更新天气预警
    partial_update: 部分更新天气预警
    destroy: 删除天气预警
    """
    queryset = Weatheralert.objects.prefetch_related(
        'alertaffectedpoi_set__poi'
    ).all()
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['level', 'status']
    search_fields = ['title', 'level']
    ordering_fields = ['alert_id', 'publish_time']
    ordering = ['-publish_time']
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'list':
            return WeatheralertListSerializer
        elif self.action == 'create':
            return WeatheralertCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return WeatheralertUpdateSerializer
        return WeatheralertSerializer
    
    @action(detail=True, methods=['get'])
    def affected_pois(self, request, pk=None):
        """
        获取预警影响的所有POI
        """
        alert = self.get_object()
        affected = alert.alertaffectedpoi_set.select_related('poi').all()
        
        serializer = AlertaffectedpoiSerializer(affected, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_poi(self, request, pk=None):
        """
        添加受影响的POI
        
        参数：
        - poi: POI ID（必填）
        """
        alert = self.get_object()
        
        data = {
            'alert': alert.alert_id,
            'poi': request.data.get('poi')
        }
        
        serializer = AlertaffectedpoiCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        affected = serializer.save()
        
        return Response({
            'message': 'POI已添加到预警',
            'data': AlertaffectedpoiSerializer(affected).data
        })
    
    @action(detail=True, methods=['delete'])
    def remove_poi(self, request, pk=None):
        """
        移除受影响的POI
        
        参数：
        - poi: POI ID（必填）
        """
        alert = self.get_object()
        poi_id = request.query_params.get('poi')
        
        if not poi_id:
            return Response(
                {'error': '请提供POI ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            affected = Alertaffectedpoi.objects.get(alert=alert, poi_id=poi_id)
            affected.delete()
            return Response({'message': 'POI已从预警中移除'})
        except Alertaffectedpoi.DoesNotExist:
            return Response(
                {'error': '该POI不在预警影响范围内'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """激活预警（设置为生效中）"""
        alert = self.get_object()
        alert.status = '生效中'
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response({
            'message': '预警已激活',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """解除预警（设置为已解除）"""
        alert = self.get_object()
        alert.status = '已解除'
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response({
            'message': '预警已解除',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def active_alerts(self, request):
        """
        获取生效中的预警
        """
        queryset = self.queryset.filter(status='生效中')
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = WeatheralertListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = WeatheralertListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_level(self, request):
        """
        按预警级别筛选
        
        参数：
        - level: 预警级别（必填，如：红色、橙色、黄色、蓝色）
        """
        level = request.query_params.get('level')
        
        if not level:
            return Response(
                {'error': '请提供预警级别'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(level__icontains=level)
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = WeatheralertListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = WeatheralertListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        预警统计信息
        
        返回：
        - total_alerts: 预警总数
        - active_alerts: 生效中的预警数
        - by_level: 按级别分组统计
        - by_status: 按状态分组统计
        """
        total_alerts = self.queryset.count()
        active_alerts = self.queryset.filter(status='生效中').count()
        
        # 按级别统计
        by_level = self.queryset.values('level').annotate(
            count=Count('alert_id')
        ).order_by('-count')
        
        # 按状态统计
        by_status = self.queryset.values('status').annotate(
            count=Count('alert_id')
        ).order_by('-count')
        
        return Response({
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'by_level': list(by_level),
            'by_status': list(by_status)
        })


class AlertaffectedpoiViewSet(viewsets.ModelViewSet):
    """
    预警影响POI视图集
    
    list: 获取预警影响POI列表
    retrieve: 获取预警影响POI详情
    create: 创建预警影响POI关联
    update: 更新预警影响POI关联
    partial_update: 部分更新预警影响POI关联
    destroy: 删除预警影响POI关联
    """
    queryset = Alertaffectedpoi.objects.select_related(
        'alert',
        'poi'
    ).all()
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['alert', 'poi']
    search_fields = ['alert__title', 'poi__poi_name']
    ordering_fields = ['a_id']
    ordering = ['a_id']
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'list':
            return AlertaffectedpoiListSerializer
        elif self.action == 'create':
            return AlertaffectedpoiCreateSerializer
        return AlertaffectedpoiSerializer
    
    @action(detail=False, methods=['get'])
    def by_alert(self, request):
        """
        按预警ID获取所有受影响POI
        
        参数：
        - alert_id: 预警ID（必填）
        """
        alert_id = request.query_params.get('alert_id')
        
        if not alert_id:
            return Response(
                {'error': '请提供预警ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(alert_id=alert_id)
        serializer = AlertaffectedpoiListSerializer(queryset, many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_poi(self, request):
        """
        按POI ID获取所有相关预警
        
        参数：
        - poi_id: POI ID（必填）
        """
        poi_id = request.query_params.get('poi_id')
        
        if not poi_id:
            return Response(
                {'error': '请提供POI ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(poi_id=poi_id)
        serializer = AlertaffectedpoiListSerializer(queryset, many=True)
        
        return Response(serializer.data)


class WeatherforecastViewSet(viewsets.ModelViewSet):
    """
    天气预报视图集
    
    list: 获取天气预报列表
    retrieve: 获取天气预报详情
    create: 创建天气预报
    update: 更新天气预报
    partial_update: 部分更新天气预报
    destroy: 删除天气预报
    """
    queryset = Weatherforecast.objects.select_related('location').all()
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location', 'forecast_date', 'condition_day']
    search_fields = ['location__location_name', 'condition_day']
    ordering_fields = ['forecast_id', 'forecast_date']
    ordering = ['forecast_date']
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'list':
            return WeatherforecastListSerializer
        elif self.action == 'create':
            return WeatherforecastCreateSerializer
        return WeatherforecastSerializer
    
    @action(detail=False, methods=['get'])
    def by_location(self, request):
        """
        按位置ID获取预报
        
        参数：
        - location_id: 位置ID（必填）
        - days: 预报天数（默认7天）
        """
        location_id = request.query_params.get('location_id')
        days = int(request.query_params.get('days', 7))
        
        if not location_id:
            return Response(
                {'error': '请提供位置ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(location_id=location_id)[:days]
        serializer = WeatherforecastSerializer(queryset, many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        获取未来的天气预报
        
        参数：
        - days: 未来天数（默认7天）
        """
        days = int(request.query_params.get('days', 7))
        today = timezone.now().date()
        
        queryset = self.queryset.filter(
            forecast_date__gte=today
        ).order_by('forecast_date')[:days]
        
        serializer = WeatherforecastSerializer(queryset, many=True)
        return Response(serializer.data)