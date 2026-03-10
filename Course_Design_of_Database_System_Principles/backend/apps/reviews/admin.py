from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Locationweather,
    Weatheralert,
    Alertaffectedpoi,
    Weatherforecast
)


class WeatherforecastInline(admin.TabularInline):
    """天气预报内联"""
    model = Weatherforecast
    extra = 0
    fields = ['forecast_date', 'temp_max', 'temp_min', 'condition_day']


class AlertaffectedpoiInline(admin.TabularInline):
    """预警影响POI内联"""
    model = Alertaffectedpoi
    extra = 0
    fields = ['poi']
    autocomplete_fields = ['poi']


@admin.register(Locationweather)
class LocationweatherAdmin(admin.ModelAdmin):
    list_display = ['location_id', 'location_name', 'weather_display', 
                    'coordinate_display', 'poi_link', 'update_time']
    list_filter = ['conditions', 'update_time']
    search_fields = ['location_name', 'poi__poi_name']
    autocomplete_fields = ['poi']
    ordering = ['-update_time']
    
    inlines = [WeatherforecastInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('location_name', 'poi')
        }),
        ('位置坐标', {
            'fields': ('longitude', 'latitude')
        }),
        ('天气信息', {
            'fields': ('temperature', 'conditions', 'update_time')
        }),
    )
    
    def weather_display(self, obj):
        """天气显示"""
        if obj.conditions and obj.temperature:
            return format_html(
                '<strong>{}</strong> <span style="color: blue;">{} ℃</span>',
                obj.conditions,
                obj.temperature
            )
        return '-'
    weather_display.short_description = '天气状况'
    
    def coordinate_display(self, obj):
        """坐标显示"""
        if obj.longitude and obj.latitude:
            return format_html(
                '<small>经度: {}<br/>纬度: {}</small>',
                obj.longitude,
                obj.latitude
            )
        return '-'
    coordinate_display.short_description = '坐标'
    
    def poi_link(self, obj):
        """POI链接"""
        if obj.poi:
            return format_html(
                '<a href="/admin/attractions/poimaster/{}/change/">{}</a>',
                obj.poi.poi_id,
                obj.poi.poi_name
            )
        return '-'
    poi_link.short_description = '关联POI'


@admin.register(Weatheralert)
class WeatheralertAdmin(admin.ModelAdmin):
    list_display = ['alert_id', 'title_display', 'level_display', 
                    'status_display', 'affected_poi_count', 'publish_time']
    list_filter = ['level', 'status', 'publish_time']
    search_fields = ['title', 'level']
    ordering = ['-publish_time']
    
    inlines = [AlertaffectedpoiInline]
    
    def title_display(self, obj):
        """标题显示"""
        return format_html('<strong>{}</strong>', obj.title)
    title_display.short_description = '预警标题'
    
    def level_display(self, obj):
        """级别显示"""
        color_map = {
            '红色': 'red',
            '橙色': 'orange',
            '黄色': '#FFD700',
            '蓝色': 'blue'
        }
        color = color_map.get(obj.level, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.level or '未指定'
        )
    level_display.short_description = '预警级别'
    
    def status_display(self, obj):
        """状态显示"""
        color = 'green' if obj.status == '生效中' else 'gray'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.status or '未指定'
        )
    status_display.short_description = '预警状态'
    
    def affected_poi_count(self, obj):
        """受影响POI数量"""
        count = obj.alertaffectedpoi_set.count()
        return format_html(
            '<span style="color: blue; font-weight: bold;">{}</span>',
            count
        )
    affected_poi_count.short_description = '受影响POI'


@admin.register(Alertaffectedpoi)
class AlertaffectedpoiAdmin(admin.ModelAdmin):
    list_display = ['a_id', 'alert_display', 'poi_display']
    list_filter = ['alert__level', 'alert__status']
    search_fields = ['alert__title', 'poi__poi_name']
    autocomplete_fields = ['alert', 'poi']
    ordering = ['a_id']
    
    def alert_display(self, obj):
        """预警显示"""
        return format_html(
            '<strong>{}</strong><br/><small style="color: {};">{}</small>',
            obj.alert.title,
            'red' if obj.alert.level == '红色' else 'orange' if obj.alert.level == '橙色' else 'gray',
            obj.alert.level or '未指定'
        )
    alert_display.short_description = '天气预警'
    
    def poi_display(self, obj):
        """POI显示"""
        return format_html(
            '<strong>{}</strong><br/><small style="color: gray;">{}</small>',
            obj.poi.poi_name,
            obj.poi.address or '无地址'
        )
    poi_display.short_description = '受影响POI'


@admin.register(Weatherforecast)
class WeatherforecastAdmin(admin.ModelAdmin):
    list_display = ['forecast_id', 'location_display', 'forecast_date', 
                    'temperature_display', 'condition_day']
    list_filter = ['forecast_date', 'condition_day']
    search_fields = ['location__location_name', 'condition_day']
    autocomplete_fields = ['location']
    ordering = ['forecast_date']
    
    def location_display(self, obj):
        """位置显示"""
        return format_html(
            '<a href="/admin/reviews/locationweather/{}/change/">{}</a>',
            obj.location.location_id,
            obj.location.location_name
        )
    location_display.short_description = '位置'
    
    def temperature_display(self, obj):
        """温度显示"""
        if obj.temp_min and obj.temp_max:
            return format_html(
                '<span style="color: blue;">{} ℃</span> ~ <span style="color: red;">{} ℃</span>',
                obj.temp_min,
                obj.temp_max
            )
        return '-'
    temperature_display.short_description = '温度范围'