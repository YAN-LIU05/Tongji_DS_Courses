from rest_framework import serializers
from .models import Hoteldetails
from apps.attractions.serializers import PoimasterSerializer, ScenicspotdetailsSerializer


class HoteldetailsSerializer(serializers.ModelSerializer):
    """酒店详情序列化器"""
    
    # 嵌套显示关联的 POI 信息
    hotel_info = PoimasterSerializer(source='hotel', read_only=True)
    
    # 嵌套显示所属景区信息
    scenic_info = ScenicspotdetailsSerializer(source='scenic_spot_detail', read_only=True)
    
    class Meta:
        model = Hoteldetails
        fields = [
            'h_id',
            'hotel',
            'hotel_info',
            'scenic_spot_detail',
            'scenic_info',
            'star_rating',
            'room_count'
        ]


class HotelListSerializer(serializers.ModelSerializer):
    """酒店列表序列化器（简化版）"""
    
    hotel_name = serializers.CharField(source='hotel.poi_name', read_only=True)
    hotel_type = serializers.CharField(source='hotel.poi_type', read_only=True)
    address = serializers.CharField(source='hotel.address', read_only=True)
    longitude = serializers.DecimalField(
        source='hotel.longitude',
        max_digits=10,
        decimal_places=6,
        read_only=True
    )
    latitude = serializers.DecimalField(
        source='hotel.latitude',
        max_digits=10,
        decimal_places=6,
        read_only=True
    )
    
    class Meta:
        model = Hoteldetails
        fields = [
            'h_id',
            'hotel_name',
            'hotel_type',
            'address',
            'longitude',
            'latitude',
            'star_rating',
            'room_count'
        ]


class HotelWithDynamicSerializer(serializers.ModelSerializer):
    """酒店带动态数据的序列化器"""
    
    hotel_info = PoimasterSerializer(source='hotel', read_only=True)
    scenic_info = ScenicspotdetailsSerializer(source='scenic_spot_detail', read_only=True)
    
    # 最新入住率数据
    latest_occupancy = serializers.SerializerMethodField()
    
    class Meta:
        model = Hoteldetails
        fields = [
            'h_id',
            'hotel_info',
            'scenic_info',
            'star_rating',
            'room_count',
            'latest_occupancy'
        ]
    
    def get_latest_occupancy(self, obj):
        """获取最新的入住率数据"""
        from apps.attractions.models import Dynamicdata
        from apps.attractions.serializers import DynamicdataSerializer
        
        latest = Dynamicdata.objects.filter(
            poi=obj.hotel
        ).order_by('-record_time').first()
        
        if latest:
            return DynamicdataSerializer(latest).data
        return None