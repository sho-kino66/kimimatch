from django.contrib import admin
from .models import Announcement,Tag,Inquiry


admin.site.register(Announcement)
admin.site.register(Tag) # Tagを登録

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    # 1. 管理画面の一覧に表示する項目
    list_display = ('created_at', 'name', 'subject', 'email')
    
    # 2. 一覧画面で内容をクリックして詳細ページへ飛べるようにする項目
    list_display_links = ('created_at', 'subject')
    
    # 3. 検索ボックスの追加（名前や件名で検索可能に）
    search_fields = ('name', 'subject', 'email', 'message')
    
    # 4. 右側に日付フィルターを追加
    list_filter = ('created_at',)
    
    # 5. 並び順を「新しい順（送信日時が遅い順）」にする
    ordering = ('-created_at',)

    # 6. 内容を編集不可（読み取り専用）にする場合は以下を追加（任意）
    # readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')