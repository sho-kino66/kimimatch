from django.contrib import admin
from .models import Company, Scout

# 企業情報の登録
admin.site.register(Company)

@admin.register(Scout)
class ScoutAdmin(admin.ModelAdmin):
    list_display = ('company', 'student', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('company__name', 'student__full_name')