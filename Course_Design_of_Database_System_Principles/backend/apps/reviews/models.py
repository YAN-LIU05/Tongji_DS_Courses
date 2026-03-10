from django.db import models
from apps.attractions.models import Poimaster


class Locationweather(models.Model):
    """位置天气表"""
    
    location_id = models.AutoField(primary_key=True, verbose_name='位置ID')
    location_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='位置名称'
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name='经度'
    )
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name='纬度'
    )
    poi = models.ForeignKey(
        Poimaster,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='关联POI'
    )
    temperature = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='温度 (℃)'
    )
    conditions = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='天气状况',
        help_text='如：晴、多云、雨'
    )
    update_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        db_table = 'locationweather'
        verbose_name = '位置天气'
        verbose_name_plural = '位置天气'
        ordering = ['-update_time']
    
    def __str__(self):
        return f"{self.location_name} - {self.conditions} {self.temperature}℃"


class Weatheralert(models.Model):
    """天气预警表"""
    
    alert_id = models.AutoField(primary_key=True, verbose_name='预警ID')
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='预警标题'
    )
    level = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='预警级别',
        help_text='如：红色、橙色、黄色、蓝色'
    )
    status = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='预警状态',
        help_text='如：生效中、已解除'
    )
    publish_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='发布时间'
    )
    
    class Meta:
        db_table = 'weatheralert'
        verbose_name = '天气预警'
        verbose_name_plural = '天气预警'
        ordering = ['-publish_time']
    
    def __str__(self):
        return f"{self.title} ({self.level})"


class Alertaffectedpoi(models.Model):
    """预警影响的POI关联表"""
    
    a_id = models.AutoField(primary_key=True, verbose_name='关联ID')
    alert = models.ForeignKey(
        Weatheralert,
        on_delete=models.CASCADE,
        verbose_name='天气预警'
    )
    poi = models.ForeignKey(
        Poimaster,
        on_delete=models.CASCADE,
        verbose_name='受影响POI'
    )
    
    class Meta:
        db_table = 'alertaffectedpoi'
        verbose_name = '预警影响POI'
        verbose_name_plural = '预警影响POI'
        unique_together = (('alert', 'poi'),)
    
    def __str__(self):
        return f"{self.alert.title} 影响 {self.poi.poi_name}"


class Weatherforecast(models.Model):
    """天气预报表"""
    
    forecast_id = models.AutoField(primary_key=True, verbose_name='预报ID')
    location = models.ForeignKey(
        Locationweather,
        on_delete=models.CASCADE,
        verbose_name='位置'
    )
    forecast_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='预报日期'
    )
    temp_max = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='最高温度 (℃)'
    )
    temp_min = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='最低温度 (℃)'
    )
    condition_day = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='白天天气',
        help_text='如：晴、多云、雨'
    )
    
    class Meta:
        db_table = 'weatherforecast'
        verbose_name = '天气预报'
        verbose_name_plural = '天气预报'
        ordering = ['forecast_date']
    
    def __str__(self):
        return f"{self.location.location_name} {self.forecast_date} 预报"