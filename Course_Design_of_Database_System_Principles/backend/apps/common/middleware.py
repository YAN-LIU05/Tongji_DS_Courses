"""
中间件
提供请求/响应的全局处理
"""
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    请求日志中间件
    记录所有API请求的详细信息
    """
    def process_request(self, request):
        """请求开始时记录"""
        request.start_time = time.time()
        
        # 记录请求信息
        logger.info(f"[Request] {request.method} {request.path} from {self.get_client_ip(request)}")
        
        return None

    def process_response(self, request, response):
        """响应时记录"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(
                f"[Response] {request.method} {request.path} "
                f"Status: {response.status_code} "
                f"Duration: {duration:.3f}s"
            )
        
        return response

    @staticmethod
    def get_client_ip(request):
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ResponseFormatMiddleware(MiddlewareMixin):
    """
    统一响应格式中间件
    将所有响应格式化为统一的JSON格式
    """
    def process_response(self, request, response):
        """格式化响应"""
        # 只处理JSON响应
        if response.get('Content-Type', '').startswith('application/json'):
            # 如果响应已经是标准格式，直接返回
            if hasattr(response, 'data') and isinstance(response.data, dict):
                if 'code' in response.data:
                    return response
        
        return response


class ExceptionMiddleware(MiddlewareMixin):
    """
    全局异常处理中间件
    捕获未被处理的异常
    """
    def process_exception(self, request, exception):
        """处理异常"""
        logger.error(f"未捕获的异常: {str(exception)}", exc_info=True)
        
        return JsonResponse({
            'code': 500,
            'message': '服务器内部错误',
            'data': None,
            'error': str(exception) if hasattr(settings, 'DEBUG') and settings.DEBUG else None
        }, status=500)


class CORSMiddleware(MiddlewareMixin):
    """
    CORS跨域中间件
    处理跨域请求
    """
    def process_response(self, request, response):
        """添加CORS头"""
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response['Access-Control-Max-Age'] = '3600'
        
        return response

    def process_request(self, request):
        """处理OPTIONS请求"""
        if request.method == 'OPTIONS':
            response = JsonResponse({'message': 'OK'})
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            return response
        
        return None


class TimezoneMiddleware(MiddlewareMixin):
    """
    时区中间件
    根据请求头设置时区
    """
    def process_request(self, request):
        """设置时区"""
        from django.utils import timezone
        
        tzname = request.META.get('HTTP_X_TIMEZONE')
        if tzname:
            try:
                import pytz
                timezone.activate(pytz.timezone(tzname))
            except Exception:
                timezone.deactivate()
        
        return None


class RequestIDMiddleware(MiddlewareMixin):
    """
    请求ID中间件
    为每个请求生成唯一ID
    """
    def process_request(self, request):
        """生成请求ID"""
        import uuid
        request.request_id = str(uuid.uuid4())
        return None

    def process_response(self, request, response):
        """添加请求ID到响应头"""
        if hasattr(request, 'request_id'):
            response['X-Request-ID'] = request.request_id
        return response