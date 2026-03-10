"""
景点模块序列化器
"""
from rest_framework import serializers
from .models import Poimaster, Dynamicdata, Scenicspotdetails
from django.utils import timezone

class PoimasterSerializer(serializers.ModelSerializer):
    """POI 主表序列化器"""
    
    class Meta:
        model = Poimaster
        fields = '__all__'
        read_only_fields = ['poi_id']


class PoimasterListSerializer(serializers.ModelSerializer):
    """POI 列表序列化器（简化版）"""
    
    class Meta:
        model = Poimaster
        fields = [
            'poi_id', 'poi_name', 'poi_type',
            'address', 'longitude', 'latitude', 'description'
        ]


class DynamicdataSerializer(serializers.ModelSerializer):
    poi_name = serializers.CharField(source='poi.poi_name', read_only=True)
    record_time = serializers.SerializerMethodField()

    class Meta:
        model = Dynamicdata
        fields = '__all__'
        read_only_fields = ['record_id']

    def get_record_time(self, obj):
        return timezone.localtime(obj.record_time).strftime('%Y-%m-%d %H:%M:%S')


class ScenicspotdetailsSerializer(serializers.ModelSerializer):
    """景点详情序列化器"""
    poi_info = PoimasterSerializer(source='scenic_spot', read_only=True)
    
    class Meta:
        model = Scenicspotdetails
        fields = '__all__'
        read_only_fields = ['s_id']


class ScenicspotdetailsCreateSerializer(serializers.ModelSerializer):
    """景点详情创建序列化器"""
    
    class Meta:
        model = Scenicspotdetails
        fields = '__all__'
        read_only_fields = ['s_id']