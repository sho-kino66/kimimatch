"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing # 3. (この後作成する)チャットアプリのルーティングをインポート

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# ↓ 2. Djangoの標準の application を django_asgi_app として保持
django_asgi_app = get_asgi_application()

# ↓ 4. WebSocket通信用の設定を追記
application = ProtocolTypeRouter({
    "http": django_asgi_app, # 通常のHTTPリクエストはDjango標準が処理
    
    "websocket": AuthMiddlewareStack( # WebSocketリクエストは
        URLRouter(
            chat.routing.websocket_urlpatterns # chat アプリの URL 設定に従う
        )
    ),
})