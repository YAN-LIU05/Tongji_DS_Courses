from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="智慧旅游平台 API",
        default_version='v1.0',
        description="""
# 智慧旅游平台 API 文档
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="dev@travel-platform.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

@require_http_methods(["GET"])
def api_root(request):
    """API 根路径"""
    return JsonResponse({
        'message': '🎉 欢迎使用旅游数据库 API',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'api': {
                'users': '/api/v1/users/',        # ← 改为 v1
                'attractions': '/api/attractions/',
                'hotels': '/api/hotels/',
                'reviews': '/api/reviews/',
                'orders': '/api/orders/',
            },
            'docs': {
                'swagger': '/swagger/',
                'redoc': '/redoc/',
            }
        },
        'status': 'running'
    })

urlpatterns = [
    # 根路径
    path('', api_root, name='api-root'),
    
    # 管理后台
    path('admin/', admin.site.urls),
    
    # API v1 路由
    path('api/v1/users/', include('apps.users.urls')),      # ← 改为 v1
    
    # 其他 API 路由
    path('api/attractions/', include('apps.attractions.urls')),
    path('api/hotels/', include('apps.hotels.urls')),
    path('api/reviews/', include('apps.reviews.urls')),
    path('api/orders/', include('apps.orders.urls')),

    # API 文档
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# 开发环境下的媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)