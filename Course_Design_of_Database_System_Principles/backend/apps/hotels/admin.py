from django.contrib import admin
from .models import Hoteldetails


@admin.register(Hoteldetails)
class HoteldetailsAdmin(admin.ModelAdmin):
    list_display = [
        'h_id',
        'get_hotel_name',
        'star_rating',
        'room_count',
        'get_scenic_spot'
    ]
    list_filter = ['star_rating', 'scenic_spot_detail']
    search_fields = [
        'hotel__poi_name',
        'hotel__address',
        'star_rating'
    ]
    raw_id_fields = ['hotel', 'scenic_spot_detail']
    
    def get_hotel_name(self, obj):
        return obj.hotel.poi_name
    get_hotel_name.short_description = '酒店名称'
    
    def get_scenic_spot(self, obj):
        if obj.scenic_spot_detail:
            return obj.scenic_spot_detail.scenic_spot.poi_name
        return '-'
    get_scenic_spot.short_description = '所属景区'