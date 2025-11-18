from django.contrib import admin
from .models import School # 1. モデルをインポート

# 2. 管理サイトに登録
admin.site.register(School)