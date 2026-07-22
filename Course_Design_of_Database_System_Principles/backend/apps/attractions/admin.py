"""
景点模块管理后台
"""
from django.contrib import admin
from .models import Poimaster, Dynamicdata, Scenicspotdetails


@admin.register(Poimaster)
class PoimasterAdmin(admin.ModelAdmin):
    """POI 主表管理"""
    list_display = ['poi_id', 'poi_name', 'poi_type', 'address']
    list_filter = ['poi_type']
    search_fields = ['poi_name', 'address', 'description']
    ordering = ['poi_id']


@admin.register(Dynamicdata)
class DynamicdataAdmin(admin.ModelAdmin):
    """动态数据管理"""
    list_display = ['record_id', 'poi', 'record_time', 'passenger_flow', 'occupancy_rate']
    list_filter = ['record_time']
    search_fields = ['poi__poi_name']
    ordering = ['-record_time']
    raw_id_fields = ['poi']


@admin.register(Scenicspotdetails)
class ScenicspotdetailsAdmin(admin.ModelAdmin):
    """景点详情管理"""
    list_display = ['s_id', 'scenic_spot', 'level', 'max_capacity']
    list_filter = ['level']
    search_fields = ['scenic_spot__poi_name']
    raw_id_fields = ['scenic_spot']