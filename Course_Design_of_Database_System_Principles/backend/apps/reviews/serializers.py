"""
天气模块序列化器
"""
from rest_framework import serializers
from django.utils import timezone
from .models import (
    Locationweather,
    Weatheralert,
    Alertaffectedpoi,
    Weatherforecast
)
from apps.attractions.models import Poimaster


class PoiSimpleSerializer(serializers.ModelSerializer):
    """POI简单信息序列化器"""
    class Meta:
        model = Poimaster
        fields = ['poi_id', 'poi_name', 'type_code', 'address', 'city_name']


class WeatherforecastSerializer(serializers.ModelSerializer):
    """天气预报序列化器"""
    location_name = serializers.CharField(source='location.location_name', read_only=True)
    temperature_range = serializers.SerializerMethodField()
    
    class Meta:
        model = Weatherforecast
        fields = '__all__'
    
    def get_temperature_range(self, obj):
        """获取温度范围"""
        if obj.temp_min and obj.temp_max:
            return f"{obj.temp_min}℃ ~ {obj.temp_max}℃"
        return None


class WeatherforecastListSerializer(serializers.ModelSerializer):
    """天气预报列表序列化器（简化版）"""
    location_name = serializers.CharField(source='location.location_name', read_only=True)
    
    class Meta:
        model = Weatherforecast
        fields = ['forecast_id', 'location', 'location_name', 'forecast_date', 
                  'temp_max', 'temp_min', 'condition_day']


class WeatherforecastCreateSerializer(serializers.ModelSerializer):
    """天气预报创建序列化器"""
    class Meta:
        model = Weatherforecast
        fields = ['location', 'forecast_date', 'temp_max', 'temp_min', 'condition_day']
    
    def validate(self, data):
        """验证温度逻辑"""
        temp_min = data.get('temp_min')
        temp_max = data.get('temp_max')
        
        if temp_min and temp_max and temp_min > temp_max:
            raise serializers.ValidationError("最低温度不能高于最高温度")
        
        return data


class AlertaffectedpoiSerializer(serializers.ModelSerializer):
    """预警影响POI序列化器"""
    alert_title = serializers.CharField(source='alert.title', read_only=True)
    alert_level = serializers.CharField(source='alert.level', read_only=True)
    poi_name = serializers.CharField(source='poi.poi_name', read_only=True)
    poi_info = PoiSimpleSerializer(source='poi', read_only=True)
    
    class Meta:
        model = Alertaffectedpoi
        fields = '__all__'
    
    def validate(self, data):
        """验证预警POI关联唯一性"""
        alert = data.get('alert')
        poi = data.get('poi')
        
        # 更新时排除当前实例
        if self.instance:
            exists = Alertaffectedpoi.objects.filter(
                alert=alert,
                poi=poi
            ).exclude(a_id=self.instance.a_id).exists()
        else:
            exists = Alertaffectedpoi.objects.filter(
                alert=alert,
                poi=poi
            ).exists()
        
        if exists:
            raise serializers.ValidationError("该预警与POI的关联已存在")
        
        return data


class WeatheralertSerializer(serializers.ModelSerializer):
    """天气预警详情序列化器"""
    affected_pois = AlertaffectedpoiSerializer(
        source='alertaffectedpoi_set',
        many=True,
        read_only=True
    )
    affected_poi_count = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Weatheralert
        fields = '__all__'
    
    def get_affected_poi_count(self, obj):
        """获取受影响POI数量"""
        return obj.alertaffectedpoi_set.count()
    
    def get_is_active(self, obj):
        """判断预警是否生效中"""
        return obj.status == '生效中' if obj.status else False


class WeatheralertListSerializer(serializers.ModelSerializer):
    """天气预警列表序列化器（简化版）"""
    affected_poi_count = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Weatheralert
        fields = ['alert_id', 'title', 'level', 'status', 'publish_time', 
                  'affected_poi_count', 'is_active']
    
    def get_affected_poi_count(self, obj):
        """获取受影响POI数量"""
        return obj.alertaffectedpoi_set.count()
    
    def get_is_active(self, obj):
        """判断预警是否生效中"""
        return obj.status == '生效中' if obj.status else False


class WeatheralertCreateSerializer(serializers.ModelSerializer):
    """天气预警创建序列化器"""
    affected_poi_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
        help_text="受影响的POI ID列表"
    )
    
    class Meta:
        model = Weatheralert
        fields = ['title', 'level', 'status', 'publish_time', 'affected_poi_ids']
    
    def create(self, validated_data):
        """创建天气预警"""
        affected_poi_ids = validated_data.pop('affected_poi_ids', [])
        
        # 如果没有提供发布时间，使用当前时间
        if not validated_data.get('publish_time'):
            validated_data['publish_time'] = timezone.now()
        
        # 创建预警
        alert = Weatheralert.objects.create(**validated_data)
        
        # 创建POI关联
        for poi_id in affected_poi_ids:
            try:
                poi = Poimaster.objects.get(poi_id=poi_id)
                Alertaffectedpoi.objects.create(alert=alert, poi=poi)
            except Poimaster.DoesNotExist:
                pass  # 忽略不存在的POI
        
        return alert


class WeatheralertUpdateSerializer(serializers.ModelSerializer):
    """天气预警更新序列化器"""
    class Meta:
        model = Weatheralert
        fields = ['title', 'level', 'status', 'publish_time']


class LocationweatherSerializer(serializers.ModelSerializer):
    """位置天气详情序列化器"""
    poi_info = PoiSimpleSerializer(source='poi', read_only=True)
    forecasts = WeatherforecastListSerializer(
        source='weatherforecast_set',
        many=True,
        read_only=True
    )
    forecast_count = serializers.SerializerMethodField()
    coordinate = serializers.SerializerMethodField()
    
    class Meta:
        model = Locationweather
        fields = '__all__'
    
    def get_forecast_count(self, obj):
        """获取预报数量"""
        return obj.weatherforecast_set.count()
    
    def get_coordinate(self, obj):
        """获取坐标"""
        if obj.longitude and obj.latitude:
            return {
                'longitude': float(obj.longitude),
                'latitude': float(obj.latitude)
            }
        return None


class LocationweatherListSerializer(serializers.ModelSerializer):
    """位置天气列表序列化器（简化版）"""
    poi_name = serializers.CharField(source='poi.poi_name', read_only=True)
    weather_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Locationweather
        fields = ['location_id', 'location_name', 'poi', 'poi_name', 
                  'temperature', 'conditions', 'update_time', 'weather_summary']
    
    def get_weather_summary(self, obj):
        """获取天气摘要"""
        if obj.conditions and obj.temperature:
            return f"{obj.conditions} {obj.temperature}℃"
        return None


class LocationweatherCreateSerializer(serializers.ModelSerializer):
    """位置天气创建序列化器"""
    class Meta:
        model = Locationweather
        fields = ['location_name', 'longitude', 'latitude', 'poi', 
                  'temperature', 'conditions', 'update_time']
    
    def validate(self, data):
        """验证坐标范围"""
        longitude = data.get('longitude')
        latitude = data.get('latitude')
        
        if longitude and (longitude < -180 or longitude > 180):
            raise serializers.ValidationError("经度必须在 -180 到 180 之间")
        
        if latitude and (latitude < -90 or latitude > 90):
            raise serializers.ValidationError("纬度必须在 -90 到 90 之间")
        
        return data


class LocationweatherUpdateSerializer(serializers.ModelSerializer):
    """位置天气更新序列化器"""
    class Meta:
        model = Locationweather
        fields = ['location_name', 'longitude', 'latitude', 'poi', 
                  'temperature', 'conditions', 'update_time']


class AlertaffectedpoiCreateSerializer(serializers.ModelSerializer):
    """预警影响POI创建序列化器"""
    class Meta:
        model = Alertaffectedpoi
        fields = ['alert', 'poi']
    
    def validate(self, data):
        """验证关联唯一性"""
        alert = data.get('alert')
        poi = data.get('poi')
        
        if Alertaffectedpoi.objects.filter(alert=alert, poi=poi).exists():
            raise serializers.ValidationError("该预警与POI的关联已存在")
        
        return data


class AlertaffectedpoiListSerializer(serializers.ModelSerializer):
    """预警影响POI列表序列化器"""
    alert_title = serializers.CharField(source='alert.title', read_only=True)
    alert_level = serializers.CharField(source='alert.level', read_only=True)
    alert_status = serializers.CharField(source='alert.status', read_only=True)
    poi_name = serializers.CharField(source='poi.poi_name', read_only=True)
    poi_address = serializers.CharField(source='poi.address', read_only=True)
    poi_city = serializers.CharField(source='poi.city_name', read_only=True)
    
    class Meta:
        model = Alertaffectedpoi
        fields = ['a_id', 'alert', 'alert_title', 'alert_level', 'alert_status',
                  'poi', 'poi_name', 'poi_address', 'poi_city']