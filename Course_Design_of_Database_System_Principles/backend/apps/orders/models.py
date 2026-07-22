from django.db import models
from apps.attractions.models import Poimaster


class Enterpriseinfo(models.Model):
    """企业信息表"""
    
    enterprise_id = models.AutoField(primary_key=True, verbose_name='企业ID')
    enterprise_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='企业名称'
    )
    enterprise_type = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='企业类型',
        help_text='如：旅行社、酒店集团、景区管理公司'
    )
    
    class Meta:
        db_table = 'enterpriseinfo'
        verbose_name = '企业信息'
        verbose_name_plural = '企业信息'
        ordering = ['enterprise_id']
    
    def __str__(self):
        return f"{self.enterprise_name} ({self.enterprise_type or '未分类'})"


class Enterprisepoilink(models.Model):
    """企业-POI 关联表"""
    
    e_id = models.AutoField(primary_key=True, verbose_name='关联ID')
    enterprise = models.ForeignKey(
        Enterpriseinfo,
        on_delete=models.CASCADE,
        verbose_name='企业'
    )
    poi = models.ForeignKey(
        Poimaster,
        on_delete=models.CASCADE,
        verbose_name='POI资源点'
    )
    relationship_type = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='关系类型',
        help_text='如：拥有、管理、合作'
    )
    
    class Meta:
        db_table = 'enterprisepoilink'
        verbose_name = '企业POI关联'
        verbose_name_plural = '企业POI关联'
        unique_together = (('enterprise', 'poi'),)
    
    def __str__(self):
        return f"{self.enterprise.enterprise_name} - {self.poi.poi_name} ({self.relationship_type or '未指定'})"