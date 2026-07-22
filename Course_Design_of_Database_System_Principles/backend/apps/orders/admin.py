from django.contrib import admin
from django.utils.html import format_html
from .models import Enterpriseinfo, Enterprisepoilink


class EnterprisepoilinkInline(admin.TabularInline):
    """企业POI关联内联"""
    model = Enterprisepoilink
    extra = 0
    fields = ['poi', 'relationship_type']
    autocomplete_fields = ['poi']


@admin.register(Enterpriseinfo)
class EnterpriseinfoAdmin(admin.ModelAdmin):
    list_display = ['enterprise_id', 'enterprise_name', 'enterprise_type', 'poi_count']
    list_filter = ['enterprise_type']
    search_fields = ['enterprise_name', 'enterprise_type']
    ordering = ['enterprise_id']
    
    inlines = [EnterprisepoilinkInline]
    
    def poi_count(self, obj):
        """POI数量"""
        count = obj.enterprisepoilink_set.count()
        return format_html(
            '<span style="color: blue; font-weight: bold;">{}</span>',
            count
        )
    poi_count.short_description = 'POI数量'


@admin.register(Enterprisepoilink)
class EnterprisepoilinkAdmin(admin.ModelAdmin):
    list_display = ['e_id', 'enterprise_display', 'poi_display', 'relationship_type_display']
    list_filter = ['relationship_type', 'enterprise__enterprise_type']
    search_fields = ['enterprise__enterprise_name', 'poi__poi_name', 'relationship_type']
    autocomplete_fields = ['enterprise', 'poi']
    ordering = ['e_id']
    
    def enterprise_display(self, obj):
        """企业显示"""
        return format_html(
            '<strong>{}</strong><br/><small style="color: gray;">{}</small>',
            obj.enterprise.enterprise_name,
            obj.enterprise.enterprise_type or '未分类'
        )
    enterprise_display.short_description = '企业'
    
    def poi_display(self, obj):
        """POI显示"""
        return format_html(
            '<strong>{}</strong><br/><small style="color: gray;">{}</small>',
            obj.poi.poi_name,
            obj.poi.address or '无地址'
        )
    poi_display.short_description = 'POI资源点'
    
    def relationship_type_display(self, obj):
        """关系类型显示"""
        color_map = {
            '拥有': 'green',
            '管理': 'blue',
            '合作': 'orange'
        }
        color = color_map.get(obj.relationship_type, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.relationship_type or '未指定'
        )
    relationship_type_display.short_description = '关系类型'