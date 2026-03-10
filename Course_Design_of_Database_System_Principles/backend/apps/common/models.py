"""
公共基类模型
所有业务模型都应该继承这些基类
"""
from django.db import models
from django.contrib.auth.models import User


class TimestampedModel(models.Model):
    """
    时间戳基类模型
    自动记录创建时间和更新时间
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
        help_text='记录创建的时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间',
        help_text='记录最后更新的时间'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteModel(models.Model):
    """
    软删除基类模型
    不真正删除数据，只标记为已删除
    """
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='是否删除',
        help_text='软删除标记，True表示已删除'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='删除时间',
        help_text='记录删除的时间'
    )

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """重写删除方法，实现软删除"""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        """真正删除记录"""
        super().delete()

    def restore(self):
        """恢复已删除的记录"""
        self.is_deleted = False
        self.deleted_at = None
        self.save()


class UserTrackingModel(models.Model):
    """
    用户追踪基类模型
    记录创建者和更新者
    """
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name='创建者'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        verbose_name='更新者'
    )

    class Meta:
        abstract = True


class BaseModel(TimestampedModel, SoftDeleteModel, UserTrackingModel):
    """
    完整的基类模型
    包含时间戳、软删除、用户追踪功能
    """
    class Meta:
        abstract = True


class StatusChoices(models.TextChoices):
    """通用状态选择"""
    ACTIVE = 'active', '启用'
    INACTIVE = 'inactive', '停用'
    PENDING = 'pending', '待审核'
    REJECTED = 'rejected', '已拒绝'


class GeoLocationModel(models.Model):
    """
    地理位置基类模型
    用于需要地理位置信息的模型
    """
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name='经度',
        help_text='地理坐标经度，东经为正，西经为负'
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name='纬度',
        help_text='地理坐标纬度，北纬为正，南纬为负'
    )
    address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='详细地址'
    )
    district = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='行政区域',
        help_text='如：浙江省杭州市西湖区'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"({self.latitude}, {self.longitude})"


class Config(BaseModel):
    """
    系统配置表
    用于存储系统级别的配置项
    """
    key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='配置键',
        help_text='配置项的唯一标识'
    )
    value = models.TextField(
        verbose_name='配置值',
        help_text='配置项的值，可以是JSON格式'
    )
    description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='配置描述'
    )
    category = models.CharField(
        max_length=50,
        default='general',
        verbose_name='配置分类',
        help_text='如：system, business, third_party等'
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name='是否公开',
        help_text='是否可以通过API公开访问'
    )

    class Meta:
        db_table = 'common_config'
        verbose_name = '系统配置'
        verbose_name_plural = verbose_name
        ordering = ['category', 'key']

    def __str__(self):
        return f"{self.category}.{self.key}"