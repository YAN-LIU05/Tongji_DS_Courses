"""
自定义渲染器
定义响应数据的渲染格式
"""
from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList


class CustomJSONRenderer(JSONRenderer):
    """
    自定义JSON渲染器
    统一响应格式
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        渲染响应数据
        
        标准响应格式:
        {
            "code": 200,
            "message": "success",
            "data": {...}
        }
        """
        response = renderer_context.get('response') if renderer_context else None
        
        # 如果已经是标准格式，直接返回
        if isinstance(data, dict) and 'code' in data:
            return super().render(data, accepted_media_type, renderer_context)
        
        # 处理错误响应
        if response and not response.status_code == 200:
            custom_data = {
                'code': response.status_code,
                'message': self.get_error_message(data),
                'data': None,
                'errors': data
            }
        else:
            # 处理成功响应
            custom_data = {
                'code': 200,
                'message': 'success',
                'data': data
            }
        
        return super().render(custom_data, accepted_media_type, renderer_context)

    @staticmethod
    def get_error_message(data):
        """提取错误信息"""
        if isinstance(data, dict):
            if 'detail' in data:
                return str(data['detail'])
            if 'message' in data:
                return str(data['message'])
        return '请求处理失败'