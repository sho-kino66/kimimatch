from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.top_page, name='top_page'),
    
    path('service/student/', views.student_service, name='student_service'),
    path('service/company/', views.company_service, name='company_service'),
    path('service/school/', views.school_service, name='school_service'),

    path('application/school/', views.SchoolApplicationView.as_view(), name='school_application'),
    path('application/company/', views.CompanyApplicationView.as_view(), name='company_application'),
    path('application/success/', views.application_success, name='application_success'),

    path('announcements/<int:pk>/', views.announcement_detail, name='announcement_detail'),
]