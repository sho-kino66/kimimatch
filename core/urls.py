from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.top_page, name='top_page'),

    # ↓↓ これらを追加 ↓↓
    path('service/student/', views.student_service, name='student_service'),
    path('service/company/', views.company_service, name='company_service'),
    path('service/school/', views.school_service, name='school_service'),

    path('announcements/<int:pk>/', views.announcement_detail, name='announcement_detail'),
]