from django.db import models
from apps.attractions.models import Poimaster, Scenicspotdetails


class Hoteldetails(models.Model):
    """酒店详情表"""
    
    h_id = models.AutoField(primary_key=True, verbose_name='酒店详情ID')
    hotel = models.OneToOneField(
        Poimaster,
        on_delete=models.CASCADE,
        verbose_name='关联POI',
        help_text='酒店ID=poi_id'
    )
    scenic_spot_detail = models.ForeignKey(
        Scenicspotdetails,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='所属景区',
        help_text='所属景区扩展ID'
    )
    star_rating = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='星级',
        help_text='如：五星级、四星级'
    )
    room_count = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='房间数量'
    )
    
    class Meta:
        db_table = 'hoteldetails'
        verbose_name = '酒店详情'
        verbose_name_plural = '酒店详情'
    
    def __str__(self):
        return f"{self.hotel.poi_name} ({self.star_rating or '未评级'})"