"""
公共过滤器
提供通用的过滤功能
"""
from django_filters import rest_framework as filters
from django.db.models import Q


class BaseFilterSet(filters.FilterSet):
    """
    基础过滤器集
    提供通用的过滤字段
    """
    # 时间范围过滤
    created_after = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='创建时间开始'
    )
    created_before = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='创建时间结束'
    )
    
    # 关键词搜索（需要在子类中定义search_fields）
    search = filters.CharFilter(
        method='filter_search',
        label='关键词搜索'
    )

    def filter_search(self, queryset, name, value):
        """
        关键词搜索
        需要在子类中定义 search_fields 列表
        """
        if not value:
            return queryset
        
        search_fields = getattr(self.Meta, 'search_fields', [])
        if not search_fields:
            return queryset
        
        q_objects = Q()
        for field in search_fields:
            q_objects |= Q(**{f"{field}__icontains": value})
        
        return queryset.filter(q_objects)


class GeoFilterSet(filters.FilterSet):
    """
    地理位置过滤器
    支持范围查询
    """
    # 经纬度范围
    min_longitude = filters.NumberFilter(
        field_name='longitude',
        lookup_expr='gte',
        label='最小经度'
    )
    max_longitude = filters.NumberFilter(
        field_name='longitude',
        lookup_expr='lte',
        label='最大经度'
    )
    min_latitude = filters.NumberFilter(
        field_name='latitude',
        lookup_expr='gte',
        label='最小纬度'
    )
    max_latitude = filters.NumberFilter(
        field_name='latitude',
        lookup_expr='lte',
        label='最大纬度'
    )
    
    # 行政区域
    district = filters.CharFilter(
        field_name='district',
        lookup_expr='icontains',
        label='行政区域'
    )


class DateRangeFilterSet(filters.FilterSet):
    """
    日期范围过滤器
    """
    date_from = filters.DateFilter(
        field_name='date',
        lookup_expr='gte',
        label='开始日期'
    )
    date_to = filters.DateFilter(
        field_name='date',
        lookup_expr='lte',
        label='结束日期'
    )
    
    # 快捷日期范围
    date_range = filters.ChoiceFilter(
        method='filter_date_range',
        label='日期范围',
        choices=[
            ('today', '今天'),
            ('yesterday', '昨天'),
            ('last_7_days', '最近7天'),
            ('last_30_days', '最近30天'),
            ('this_month', '本月'),
            ('last_month', '上月'),
        ]
    )

    def filter_date_range(self, queryset, name, value):
        """快捷日期范围过滤"""
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        now = timezone.now()
        today = now.date()
        
        if value == 'today':
            return queryset.filter(created_at__date=today)
        elif value == 'yesterday':
            yesterday = today - timedelta(days=1)
            return queryset.filter(created_at__date=yesterday)
        elif value == 'last_7_days':
            start_date = today - timedelta(days=7)
            return queryset.filter(created_at__date__gte=start_date)
        elif value == 'last_30_days':
            start_date = today - timedelta(days=30)
            return queryset.filter(created_at__date__gte=start_date)
        elif value == 'this_month':
            return queryset.filter(
                created_at__year=today.year,
                created_at__month=today.month
            )
        elif value == 'last_month':
            first_day = today.replace(day=1)
            last_month = first_day - timedelta(days=1)
            return queryset.filter(
                created_at__year=last_month.year,
                created_at__month=last_month.month
            )
        
        return queryset