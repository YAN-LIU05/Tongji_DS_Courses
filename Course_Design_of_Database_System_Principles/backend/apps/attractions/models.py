from django.db import models


class Poimaster(models.Model):
    """POI 主表 - 所有旅游资源点的基础信息"""
    
    poi_id = models.AutoField(primary_key=True, verbose_name='资源点ID')
    poi_name = models.CharField(max_length=255, verbose_name='资源点名称')
    poi_type = models.CharField(
        max_length=100,
        verbose_name='资源点类型',
        help_text='如：景区、酒店、餐厅等'
    )
    address = models.CharField(max_length=500, blank=True, null=True, verbose_name='地址')
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
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    
    class Meta:
        db_table = 'poimaster'
        verbose_name = 'POI 资源点'
        verbose_name_plural = 'POI 资源点'
        ordering = ['poi_id']
    
    def __str__(self):
        return f"{self.poi_name} ({self.poi_type})"


class Scenicspotdetails(models.Model):
    """景区详情表"""
    
    s_id = models.AutoField(primary_key=True, verbose_name='景区详情ID')
    scenic_spot = models.OneToOneField(
        Poimaster,
        on_delete=models.CASCADE,
        verbose_name='关联POI',
        help_text='景区ID=poi_id'
    )
    level = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='景区级别',
        help_text='如：5A、4A'
    )
    max_capacity = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='最大承载量'
    )
    
    class Meta:
        db_table = 'scenicspotdetails'
        verbose_name = '景区详情'
        verbose_name_plural = '景区详情'
    
    def __str__(self):
        return f"{self.scenic_spot.poi_name} 详情"


class Dynamicdata(models.Model):
    """动态数据表 - 实时客流、入住率等"""
    
    record_id = models.AutoField(primary_key=True, verbose_name='记录ID')
    poi = models.ForeignKey(
        Poimaster,
        on_delete=models.CASCADE,
        verbose_name='关联POI'
    )
    record_time = models.DateTimeField(verbose_name='记录时间')
    passenger_flow = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='客流量'
    )
    occupancy_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='入住率/占用率',
        help_text='百分比，如 85.50 表示 85.5%'
    )
    
    class Meta:
        db_table = 'dynamicdata'
        verbose_name = '动态数据'
        verbose_name_plural = '动态数据'
        ordering = ['-record_time']
    
    def __str__(self):
        return f"{self.poi.poi_name} - {self.record_time.strftime('%Y-%m-%d %H:%M')}"