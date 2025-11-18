from django.urls import path  # ← re_path から path に変更

from . import consumers

websocket_urlpatterns = [
    # ↓ 'test/' を削除し、<int:room_id> をキャプチャする ↓
    path('ws/chat/room/<int:room_id>/', consumers.ChatConsumer.as_asgi()),
]