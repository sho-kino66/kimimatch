from django.contrib import admin
from .models import Student, Teacher, CompanyRepresentative,FavoriteCompany

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    # 一覧画面に表示する項目を指定
    list_display = ('full_name', 'school', 'grade')
    # 検索ボックスを設置
    search_fields = ('full_name', 'school__name')

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'school', 'subject')
    search_fields = ('full_name', 'school__name')

# admin.site.register(Student) ← @admin.registerを使ったので不要
# admin.site.register(Teacher) ← @admin.registerを使ったので不要

@admin.register(CompanyRepresentative)
class CompanyRepresentativeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'company', 'department')
    search_fields = ('full_name', 'company__name')

@admin.register(FavoriteCompany)
class FavoriteCompanyAdmin(admin.ModelAdmin):
    list_display = ('student', 'company', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('student__full_name', 'company__name')