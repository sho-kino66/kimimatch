"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include  # include をまとめてインポート
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # 'accounts/' で始まるURLは、accountsアプリのurls.pyを見に行く
    path('accounts/', include('accounts.urls', namespace='accounts')), 

    # 'portfolios/' で始まるURLは、portfoliosアプリのurls.pyを見に行く
    path('portfolios/', include('portfolios.urls', namespace='portfolios')),

    # 'companies/' で始まるURLは、companiesアプリのurls.pyを見に行く
    path('companies/', include('companies.urls', namespace='companies')),

    # 'schools/' で始まるURLは、schoolsアプリのurls.pyを見に行く
    path('schools/', include('schools.urls')),

    # 'chat/' で始まるURLは、chatアプリのurls.pyを見に行く
    path('chat/', include('chat.urls', namespace='chat')),

    # お知らせやトップページは core アプリが担当
    # 空文字 '' にすることで、ルートURL（http://127.0.0.1:8000/）へのアクセスも core.urls で処理します
    path('', include('core.urls')), 
]

# (開発環境でのみ、メディアファイルを提供するための設定)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)