"""
分页配置
提供多种分页方式
"""
from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
    CursorPagination
)
from rest_framework.response import Response
from collections import OrderedDict


class StandardResultPagination(PageNumberPagination):
    """
    标准分页
    使用页码进行分页
    
    请求示例：
    GET /api/resource/?page=2&page_size=20
    """
    page_size = 20  # 默认每页显示20条
    page_size_query_param = 'page_size'  # 允许客户端自定义每页数量
    max_page_size = 100  # 每页最大数量
    page_query_param = 'page'  # 页码参数名

    def get_paginated_response(self, data):
        """自定义分页响应格式"""
        return Response(OrderedDict([
            ('code', 200),
            ('message', 'success'),
            ('data', OrderedDict([
                ('count', self.page.paginator.count),  # 总记录数
                ('total_pages', self.page.paginator.num_pages),  # 总页数
                ('current_page', self.page.number),  # 当前页码
                ('page_size', self.get_page_size(self.request)),  # 每页数量
                ('next', self.get_next_link()),  # 下一页链接
                ('previous', self.get_previous_link()),  # 上一页链接
                ('results', data)  # 数据列表
            ]))
        ]))


class LargeResultPagination(PageNumberPagination):
    """
    大数据量分页
    适用于数据量较大的场景
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


class SmallResultPagination(PageNumberPagination):
    """
    小数据量分页
    适用于移动端等场景
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """
    偏移量分页
    使用limit和offset进行分页
    
    请求示例：
    GET /api/resource/?limit=20&offset=40
    """
    default_limit = 20
    max_limit = 100
    limit_query_param = 'limit'
    offset_query_param = 'offset'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('code', 200),
            ('message', 'success'),
            ('data', OrderedDict([
                ('count', self.count),
                ('limit', self.limit),
                ('offset', self.offset),
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link()),
                ('results', data)
            ]))
        ]))


class CustomCursorPagination(CursorPagination):
    """
    游标分页
    适用于实时数据流，性能最好
    
    请求示例：
    GET /api/resource/?cursor=cD0yMDIz...
    """
    page_size = 20
    ordering = '-created_at'  # 排序字段
    cursor_query_param = 'cursor'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('code', 200),
            ('message', 'success'),
            ('data', OrderedDict([
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link()),
                ('results', data)
            ]))
        ]))


class NoPagination(PageNumberPagination):
    """
    不分页
    返回所有数据（慎用）
    """
    page_size = None

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('code', 200),
            ('message', 'success'),
            ('data', OrderedDict([
                ('count', len(data)),
                ('results', data)
            ]))
        ]))