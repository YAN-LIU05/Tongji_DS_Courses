"""
订单模块序列化器
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Enterpriseinfo, Enterprisepoilink
from apps.attractions.models import Poimaster


class UserSimpleSerializer(serializers.ModelSerializer):
    """用户简单信息序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class PoiSimpleSerializer(serializers.ModelSerializer):
    """POI简单信息序列化器"""
    class Meta:
        model = Poimaster
        fields = ['poi_id', 'poi_name', 'type_code', 'address', 'city_name']


class EnterprisepoilinkSerializer(serializers.ModelSerializer):
    """企业POI关联序列化器"""
    enterprise_name = serializers.CharField(source='enterprise.enterprise_name', read_only=True)
    poi_name = serializers.CharField(source='poi.poi_name', read_only=True)
    poi_info = PoiSimpleSerializer(source='poi', read_only=True)
    
    class Meta:
        model = Enterprisepoilink
        fields = '__all__'
    
    def validate(self, data):
        """验证企业POI关联唯一性"""
        enterprise = data.get('enterprise')
        poi = data.get('poi')
        
        # 更新时排除当前实例
        if self.instance:
            exists = Enterprisepoilink.objects.filter(
                enterprise=enterprise,
                poi=poi
            ).exclude(e_id=self.instance.e_id).exists()
        else:
            exists = Enterprisepoilink.objects.filter(
                enterprise=enterprise,
                poi=poi
            ).exists()
        
        if exists:
            raise serializers.ValidationError("该企业与POI的关联已存在")
        
        return data


class EnterpriseinfoSerializer(serializers.ModelSerializer):
    """企业信息详情序列化器"""
    poi_links = EnterprisepoilinkSerializer(
        source='enterprisepoilink_set',
        many=True,
        read_only=True
    )
    poi_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Enterpriseinfo
        fields = '__all__'
    
    def get_poi_count(self, obj):
        """获取关联POI数量"""
        return obj.enterprisepoilink_set.count()


class EnterpriseinfoListSerializer(serializers.ModelSerializer):
    """企业信息列表序列化器（简化版）"""
    poi_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Enterpriseinfo
        fields = ['enterprise_id', 'enterprise_name', 'enterprise_type', 'poi_count']
    
    def get_poi_count(self, obj):
        """获取关联POI数量"""
        return obj.enterprisepoilink_set.count()


class EnterpriseinfoCreateSerializer(serializers.ModelSerializer):
    """企业信息创建序列化器"""
    poi_links_data = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        write_only=True,
        help_text="POI关联列表，格式: [{'poi': poi_id, 'relationship_type': 'xxx'}]"
    )
    
    class Meta:
        model = Enterpriseinfo
        fields = ['enterprise_name', 'enterprise_type', 'poi_links_data']
    
    def create(self, validated_data):
        """创建企业信息"""
        poi_links_data = validated_data.pop('poi_links_data', [])
        
        # 创建企业
        enterprise = Enterpriseinfo.objects.create(**validated_data)
        
        # 创建POI关联
        for link_data in poi_links_data:
            poi_id = link_data.get('poi')
            relationship_type = link_data.get('relationship_type')
            
            try:
                poi = Poimaster.objects.get(poi_id=poi_id)
                Enterprisepoilink.objects.create(
                    enterprise=enterprise,
                    poi=poi,
                    relationship_type=relationship_type
                )
            except Poimaster.DoesNotExist:
                pass  # 忽略不存在的POI
        
        return enterprise


class EnterpriseinfoUpdateSerializer(serializers.ModelSerializer):
    """企业信息更新序列化器"""
    class Meta:
        model = Enterpriseinfo
        fields = ['enterprise_name', 'enterprise_type']


class EnterprisepoilinkCreateSerializer(serializers.ModelSerializer):
    """企业POI关联创建序列化器"""
    class Meta:
        model = Enterprisepoilink
        fields = ['enterprise', 'poi', 'relationship_type']
    
    def validate(self, data):
        """验证关联唯一性"""
        enterprise = data.get('enterprise')
        poi = data.get('poi')
        
        if Enterprisepoilink.objects.filter(enterprise=enterprise, poi=poi).exists():
            raise serializers.ValidationError("该企业与POI的关联已存在")
        
        return data


class EnterprisepoilinkListSerializer(serializers.ModelSerializer):
    """企业POI关联列表序列化器"""
    enterprise_name = serializers.CharField(source='enterprise.enterprise_name', read_only=True)
    enterprise_type = serializers.CharField(source='enterprise.enterprise_type', read_only=True)
    poi_name = serializers.CharField(source='poi.poi_name', read_only=True)
    poi_address = serializers.CharField(source='poi.address', read_only=True)
    poi_city = serializers.CharField(source='poi.city_name', read_only=True)
    
    class Meta:
        model = Enterprisepoilink
        fields = ['e_id', 'enterprise', 'enterprise_name', 'enterprise_type',
                  'poi', 'poi_name', 'poi_address', 'poi_city', 'relationship_type']