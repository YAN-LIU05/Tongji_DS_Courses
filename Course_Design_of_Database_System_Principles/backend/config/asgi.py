"""
ASGI config for tourism project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# 设置默认配置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Django ASGI application
django_asgi_app = get_asgi_application()

# 如果需要WebSocket支持，可以使用Channels
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# import apps.common.routing

# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             apps.common.routing.websocket_urlpatterns
#         )
#     ),
# })

application = django_asgi_app

print("✅ ASGI应用启动成功")