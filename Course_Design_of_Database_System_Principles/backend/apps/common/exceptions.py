"""
异常处理
统一的异常处理和错误响应
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework.exceptions import (
    APIException,
    ValidationError,
    PermissionDenied,
    NotAuthenticated,
    NotFound
)
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    自定义异常处理器
    统一错误响应格式
    """
    # 调用DRF默认的异常处理器
    response = exception_handler(exc, context)

    # 如果DRF没有处理这个异常，我们自己处理
    if response is None:
        if isinstance(exc, DjangoValidationError):
            response = Response(
                {
                    'code': 400,
                    'message': '数据验证失败',
                    'data': None,
                    'errors': exc.messages
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, Http404):
            response = Response(
                {
                    'code': 404,
                    'message': '资源未找到',
                    'data': None
                },
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            # 未知异常，记录日志
            logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
            response = Response(
                {
                    'code': 500,
                    'message': '服务器内部错误',
                    'data': None,
                    'detail': str(exc) if settings.DEBUG else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # 统一响应格式
    if response is not None:
        custom_response_data = {
            'code': response.status_code,
            'message': get_error_message(exc),
            'data': None
        }

        # 添加详细错误信息
        if hasattr(exc, 'detail'):
            custom_response_data['errors'] = response.data

        response.data = custom_response_data

    return response


def get_error_message(exc):
    """
    获取友好的错误信息
    """
    if isinstance(exc, NotAuthenticated):
        return '身份认证失败，请先登录'
    elif isinstance(exc, PermissionDenied):
        return '权限不足，无法访问此资源'
    elif isinstance(exc, NotFound):
        return '请求的资源不存在'
    elif isinstance(exc, ValidationError):
        return '数据验证失败'
    elif isinstance(exc, BusinessException):
        return exc.message
    else:
        return '请求处理失败'


class BusinessException(APIException):
    """
    业务异常基类
    用于抛出业务逻辑相关的异常
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '业务处理失败'
    default_code = 'business_error'

    def __init__(self, message=None, code=None, status_code=None):
        if message is not None:
            self.message = message
            self.detail = message
        else:
            self.message = self.default_detail

        if code is not None:
            self.code = code
        else:
            self.code = self.default_code

        if status_code is not None:
            self.status_code = status_code


class ResourceNotFoundException(BusinessException):
    """资源未找到异常"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = '请求的资源不存在'
    default_code = 'resource_not_found'


class ResourceConflictException(BusinessException):
    """资源冲突异常"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = '资源已存在或发生冲突'
    default_code = 'resource_conflict'


class InvalidParameterException(BusinessException):
    """无效参数异常"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '请求参数无效'
    default_code = 'invalid_parameter'


class ExternalServiceException(BusinessException):
    """外部服务异常"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = '外部服务调用失败'
    default_code = 'external_service_error'


class DataIntegrityException(BusinessException):
    """数据完整性异常"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '数据完整性校验失败'
    default_code = 'data_integrity_error'


class RateLimitExceededException(BusinessException):
    """频率限制异常"""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = '请求过于频繁，请稍后再试'
    default_code = 'rate_limit_exceeded'