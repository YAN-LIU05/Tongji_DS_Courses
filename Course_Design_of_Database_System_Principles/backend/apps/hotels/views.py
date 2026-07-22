"""
酒店模块视图
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly  # ✅ 改用这个
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg

from .models import Hoteldetails
from .serializers import (
    HoteldetailsSerializer,
    HotelListSerializer,
    HotelWithDynamicSerializer
)


class HoteldetailsViewSet(viewsets.ModelViewSet):
    """
    酒店详情视图集
    """
    queryset = Hoteldetails.objects.select_related(
        'hotel', 
        'scenic_spot_detail',
        'scenic_spot_detail__scenic_spot'
    ).all()
    
    permission_classes = [IsAuthenticatedOrReadOnly]  # ✅ 和 attractions 一样
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['star_rating', 'scenic_spot_detail']
    search_fields = ['hotel__poi_name', 'hotel__address', 'star_rating']
    ordering_fields = ['h_id', 'room_count']
    ordering = ['h_id']
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'list':
            return HotelListSerializer
        elif self.action == 'with_dynamic':
            return HotelWithDynamicSerializer
        return HoteldetailsSerializer
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        搜索酒店
        
        参数：
        - q: 搜索关键词
        - star_rating: 星级
        - scenic_id: 所属景区ID
        """
        queryset = self.get_queryset()
        
        # 关键词搜索
        q = request.query_params.get('q', '')
        if q:
            queryset = queryset.filter(
                Q(hotel__poi_name__icontains=q) |
                Q(hotel__address__icontains=q) |
                Q(star_rating__icontains=q)
            )
        
        # 星级筛选
        star_rating = request.query_params.get('star_rating')
        if star_rating:
            queryset = queryset.filter(star_rating=star_rating)
        
        # 景区筛选
        scenic_id = request.query_params.get('scenic_id')
        if scenic_id:
            queryset = queryset.filter(scenic_spot_detail_id=scenic_id)
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def star_ratings(self, request):
        """获取所有星级分类"""
        ratings = Hoteldetails.objects.values_list(
            'star_rating', flat=True
        ).distinct().order_by('star_rating')
        return Response(list(filter(None, ratings)))
    
    @action(detail=True, methods=['get'])
    def nearby(self, request, pk=None):
        """
        获取附近的酒店
        
        参数：
        - radius: 半径（公里），默认 5
        - star_rating: 星级（可选）
        """
        hotel = self.get_object()
        
        if not hotel.hotel.latitude or not hotel.hotel.longitude:
            return Response(
                {'error': '该酒店没有坐标信息'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        radius = float(request.query_params.get('radius', 5))
        
        # 简单的经纬度范围计算（1度约等于111公里）
        lat_range = radius / 111.0
        lng_range = radius / (111.0 * abs(float(hotel.hotel.latitude)))
        
        nearby_hotels = Hoteldetails.objects.filter(
            hotel__latitude__range=(
                float(hotel.hotel.latitude) - lat_range,
                float(hotel.hotel.latitude) + lat_range
            ),
            hotel__longitude__range=(
                float(hotel.hotel.longitude) - lng_range,
                float(hotel.hotel.longitude) + lng_range
            )
        ).exclude(h_id=hotel.h_id).select_related('hotel')[:20]
        
        # 可选的星级筛选
        star_rating = request.query_params.get('star_rating')
        if star_rating:
            nearby_hotels = nearby_hotels.filter(star_rating=star_rating)
        
        serializer = HotelListSerializer(nearby_hotels, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_star(self, request):
        """
        按星级筛选酒店
        
        参数：
        - star_rating: 星级（如：五星级、四星级）
        """
        star_rating = request.query_params.get('star_rating')
        if not star_rating:
            return Response(
                {'error': '缺少 star_rating 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        hotels = self.queryset.filter(star_rating=star_rating)
        
        # 分页
        page = self.paginate_queryset(hotels)
        if page is not None:
            serializer = HotelListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = HotelListSerializer(hotels, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_scenic(self, request):
        """
        按所属景区筛选酒店
        
        参数：
        - scenic_id: 景区详情ID
        """
        scenic_id = request.query_params.get('scenic_id')
        if not scenic_id:
            return Response(
                {'error': '缺少 scenic_id 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        hotels = self.queryset.filter(scenic_spot_detail_id=scenic_id)
        
        # 分页
        page = self.paginate_queryset(hotels)
        if page is not None:
            serializer = HotelListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = HotelListSerializer(hotels, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def with_dynamic(self, request, pk=None):
        """
        获取酒店详情（含最新动态数据）
        
        返回酒店信息和最新的入住率、客流量等数据
        """
        hotel = self.get_object()
        serializer = HotelWithDynamicSerializer(hotel)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def high_star(self, request):
        """
        获取高星级酒店（四星级及以上）
        """
        high_star_hotels = self.queryset.filter(
            Q(star_rating__icontains='五星') | Q(star_rating__icontains='四星')
        )
        
        # 分页
        page = self.paginate_queryset(high_star_hotels)
        if page is not None:
            serializer = HotelListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = HotelListSerializer(high_star_hotels, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        获取可用酒店（入住率 < 指定阈值）
        
        参数：
        - threshold: 入住率阈值（默认 90）
        """
        from apps.attractions.models import Dynamicdata
        from django.db.models import Max
        
        threshold = float(request.query_params.get('threshold', 90))
        
        # 获取每个酒店 POI 的最新动态数据
        latest_data = Dynamicdata.objects.filter(
            poi__hotel__isnull=False,
            occupancy_rate__lt=threshold
        ).values('poi').annotate(
            latest_time=Max('record_time')
        )
        
        # 获取这些 POI 对应的酒店
        poi_ids = [item['poi'] for item in latest_data]
        available_hotels = self.queryset.filter(hotel_id__in=poi_ids)
        
        # 分页
        page = self.paginate_queryset(available_hotels)
        if page is not None:
            serializer = HotelListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = HotelListSerializer(available_hotels, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        酒店统计信息
        
        返回：
        - total_hotels: 总酒店数
        - star_distribution: 按星级分布
        - total_rooms: 总房间数
        - average_occupancy_rate: 平均入住率
        """
        from apps.attractions.models import Dynamicdata
        
        total_hotels = self.queryset.count()
        
        # 按星级分布
        star_distribution = self.queryset.values('star_rating').annotate(
            count=Count('h_id')
        ).order_by('-count')
        
        # 总房间数
        total_rooms = self.queryset.aggregate(
            total=Sum('room_count')
        )['total'] or 0
        
        # 平均入住率（基于最新动态数据）
        avg_occupancy = Dynamicdata.objects.filter(
            poi__hotel__isnull=False
        ).aggregate(
            avg=Avg('occupancy_rate')
        )['avg'] or 0
        
        return Response({
            'total_hotels': total_hotels,
            'star_distribution': list(star_distribution),
            'total_rooms': total_rooms,
            'average_occupancy_rate': round(float(avg_occupancy), 2)
        })