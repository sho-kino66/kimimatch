from django.urls import path
from . import views 

app_name = 'companies' # app_name はOKです

urlpatterns = [
    # 企業一覧
    path('list/', views.CompanyListView.as_view(), name='list'),
    
    # 企業詳細
    path('<int:pk>/', views.CompanyDetailView.as_view(), name='detail'),
    
    path('<int:company_pk>/add_favorite/', views.add_favorite, name='add_favorite'),
    path('<int:company_pk>/remove_favorite/', views.remove_favorite, name='remove_favorite'),
    path('scout_list/', views.ScoutedStudentListView.as_view(), name='scout_list'),
]