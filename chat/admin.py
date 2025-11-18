from django.contrib import admin
from .models import ChatRoom, ChatMessage

class ChatMessageInline(admin.TabularInline):
    """
    ChatRoom の詳細ページで、関連する ChatMessage を
    一覧表示・編集できるようにする
    """
    model = ChatMessage
    extra = 1 # 新規追加用の空欄を1つ表示

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants', 'created_at')
    inlines = [ChatMessageInline] # ↑のインライン設定を適用

    def get_participants(self, obj):
        # 参加者一覧をカンマ区切りで表示
        return ", ".join([user.username for user in obj.participants.all()])
    get_participants.short_description = 'Participants'

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('author', 'room', 'content_preview', 'timestamp')
    list_filter = ('room', 'timestamp')
    search_fields = ('author__username', 'content')

    def content_preview(self, obj):
        return obj.content[:30] # 内容を30文字だけプレビュー
    content_preview.short_description = 'Content'
