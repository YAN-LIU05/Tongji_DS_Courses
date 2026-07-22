"""
公共序列化器
提供通用的序列化器基类和混入类
"""
from rest_framework import serializers
from django.contrib.auth.models import User


class TimestampedSerializer(serializers.ModelSerializer):
    """
    时间戳序列化器
    自动处理时间字段的序列化
    """
    created_at = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S',
        read_only=True
    )
    updated_at = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S',
        read_only=True
    )


class UserTrackingSerializer(serializers.ModelSerializer):
    """
    用户追踪序列化器
    自动处理创建者和更新者的序列化
    """
    created_by_name = serializers.CharField(
        source='created_by.username',
        read_only=True,
        allow_null=True
    )
    updated_by_name = serializers.CharField(
        source='updated_by.username',
        read_only=True,
        allow_null=True
    )


class BaseSerializer(TimestampedSerializer, UserTrackingSerializer):
    """
    基础序列化器
    整合时间戳和用户追踪功能
    """
    class Meta:
        fields = '__all__'


class GeoLocationSerializer(serializers.Serializer):
    """
    地理位置序列化器
    """
    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text='经度'
    )
    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text='纬度'
    )
    address = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text='详细地址'
    )
    district = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text='行政区域'
    )


class DynamicFieldsSerializerMixin:
    """
    动态字段序列化器混入类
    允许通过请求参数动态选择返回的字段
    
    使用方式：
    GET /api/resource/?fields=id,name,created_at
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not hasattr(self, 'context'):
            return

        request = self.context.get('request')
        if not request:
            return

        # 获取fields参数
        fields_param = request.query_params.get('fields')
        if fields_param:
            fields = fields_param.split(',')
            allowed = set(fields)
            existing = set(self.fields.keys())
            
            # 移除不需要的字段
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class BulkCreateSerializer(serializers.ListSerializer):
    """
    批量创建序列化器
    支持一次性创建多条记录
    """
    def create(self, validated_data):
        results = [
            self.child.create(attrs) for attrs in validated_data
        ]
        return results

    def update(self, instance, validated_data):
        # 批量更新逻辑
        result_map = {item.id: item for item in instance}
        results = []
        
        for item_data in validated_data:
            item_id = item_data.get('id')
            if item_id and item_id in result_map:
                item = result_map[item_id]
                results.append(self.child.update(item, item_data))
        
        return results


class ReadOnlySerializer(serializers.ModelSerializer):
    """
    只读序列化器
    用于展示数据，不允许创建或更新
    """
    def create(self, validated_data):
        raise serializers.ValidationError("不支持创建操作")

    def update(self, instance, validated_data):
        raise serializers.ValidationError("不支持更新操作")


class ConfigSerializer(serializers.ModelSerializer):
    """
    系统配置序列化器
    """
    from .models import Config
    
    class Meta:
        model = Config
        fields = [
            'id', 'key', 'value', 'description', 
            'category', 'is_public',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmptySerializer(serializers.Serializer):
    """
    空序列化器
    用于不需要输入参数的接口
    """
    pass