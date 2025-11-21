from django.contrib import admin
from .models import Company, Scout,CompanyTag #CompanyTag追加

# 1. タグのインライン設定
class CompanyTagInline(admin.TabularInline):
    model = CompanyTag
    extra = 1

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry')
    # ★ この行がないと画面に表示されません！
    inlines = [CompanyTagInline]

@admin.register(Scout)
class ScoutAdmin(admin.ModelAdmin):
    list_display = ('company', 'student', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('company__name', 'student__full_name')