from django.urls import path
from . import views

# ★ これが重要です。テンプレートで {% url 'core:announcement_detail' %} と書くために必要です。
app_name = 'core'

urlpatterns = [
    # トップページ (http://127.0.0.1:8000/)
    path('', views.top_page, name='top_page'),

    # お知らせ詳細ページ (http://127.0.0.1:8000/core/announcements/1/ など)
    # ※ config/urls.py で path('core/', include('core.urls')) としている場合
    path('announcements/<int:pk>/', views.announcement_detail, name='announcement_detail'),
]