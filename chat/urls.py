from django.urls import path
from . import views # (この後作成する views.py)

app_name = 'chat'

urlpatterns = [
    # チャットテスト用のページURL
    path('test/', views.chat_test_room, name='chat_test_room'),
    path('start/<int:user_id>/', views.start_chat, name='start_chat'),
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('list/', views.ChatRoomListView.as_view(), name='chat_list'),
]