from django.contrib import admin
from .models import Announcement, Tag, Inquiry, SchoolApplication, CompanyApplication

admin.site.register(Announcement)
admin.site.register(Tag)

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'name', 'subject', 'email')
    list_display_links = ('created_at', 'subject')
    search_fields = ('name', 'subject', 'email', 'message')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

# --- 学校申し込みの管理画面設定 ---
@admin.register(SchoolApplication)
class SchoolApplicationAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'school_name', 'contact_name', 'email', 'phone')
    list_display_links = ('created_at', 'school_name')
    search_fields = ('school_name', 'contact_name', 'email', 'address')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

# --- 企業申し込みの管理画面設定 ---
@admin.register(CompanyApplication)
class CompanyApplicationAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'company_name', 'contact_name', 'email', 'phone')
    list_display_links = ('created_at', 'company_name')
    search_fields = ('company_name', 'contact_name', 'email', 'address')
    list_filter = ('created_at',)
    ordering = ('-created_at',)