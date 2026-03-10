"""
数据验证器
提供通用的数据验证规则
"""
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re


def validate_phone_number(value):
    """
    验证手机号
    支持中国大陆手机号
    """
    pattern = r'^1[3-9]\d{9}$'
    if not re.match(pattern, str(value)):
        raise ValidationError('请输入有效的手机号码')


def validate_id_card(value):
    """
    验证身份证号
    支持15位和18位身份证
    """
    pattern = r'(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)'
    if not re.match(pattern, str(value)):
        raise ValidationError('请输入有效的身份证号码')


def validate_longitude(value):
    """验证经度（-180 到 180）"""
    try:
        lon = float(value)
        if not -180 <= lon <= 180:
            raise ValidationError('经度必须在-180到180之间')
    except (ValueError, TypeError):
        raise ValidationError('经度必须是有效的数字')


def validate_latitude(value):
    """验证纬度（-90 到 90）"""
    try:
        lat = float(value)
        if not -90 <= lat <= 90:
            raise ValidationError('纬度必须在-90到90之间')
    except (ValueError, TypeError):
        raise ValidationError('纬度必须是有效的数字')


def validate_positive_number(value):
    """验证正数"""
    try:
        num = float(value)
        if num <= 0:
            raise ValidationError('必须是正数')
    except (ValueError, TypeError):
        raise ValidationError('必须是有效的数字')


def validate_percentage(value):
    """验证百分比（0-100）"""
    try:
        percent = float(value)
        if not 0 <= percent <= 100:
            raise ValidationError('百分比必须在0到100之间')
    except (ValueError, TypeError):
        raise ValidationError('百分比必须是有效的数字')


def validate_json_format(value):
    """验证JSON格式"""
    import json
    try:
        json.loads(value)
    except (json.JSONDecodeError, TypeError):
        raise ValidationError('必须是有效的JSON格式')


def validate_url_or_path(value):
    """验证URL或文件路径"""
    url_pattern = r'^https?://'
    path_pattern = r'^(/|[a-zA-Z]:\\)'
    
    if not (re.match(url_pattern, value) or re.match(path_pattern, value)):
        raise ValidationError('必须是有效的URL或文件路径')


# 预定义的正则验证器
ChineseNameValidator = RegexValidator(
    regex=r'^[\u4e00-\u9fa5·]{2,20}$',
    message='请输入有效的中文姓名（2-20个汉字）'
)

EnglishNameValidator = RegexValidator(
    regex=r'^[a-zA-Z\s]{2,50}$',
    message='请输入有效的英文姓名（2-50个字母）'
)

PostalCodeValidator = RegexValidator(
    regex=r'^\d{6}$',
    message='请输入有效的邮政编码（6位数字）'
)

UnifiedSocialCreditCodeValidator = RegexValidator(
    regex=r'^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$',
    message='请输入有效的统一社会信用代码'
)