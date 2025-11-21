from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    # 認証系 (login, logout, password_change 等)
    path('', include('django.contrib.auth.urls')),

    # 登録タイプ選択画面
    path('signup/', views.signup_type_select, name='signup_type_select'),
    
    # 新規登録画面
    path('signup/student/', views.StudentSignUpView.as_view(), name='signup_student'),
    path('signup/teacher/', views.TeacherSignUpView.as_view(), name='signup_teacher'),
    path('signup/company/', views.CompanyRepresentativeSignUpView.as_view(), name='signup_company'),

    # メインメニュー・マイページ
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my_page/', views.my_page, name='my_page'),

    # 一覧画面
    path('teacher/student_list/', views.TeacherStudentListView.as_view(), name='teacher_student_list'),
    path('company/student_list/', views.CompanyStudentListView.as_view(), name='company_student_list'),
    path('favorites/', views.FavoriteCompanyListView.as_view(), name='favorite_list'),

    # 詳細・アクション
    path('student/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('student/<int:student_pk>/add_scout/', views.add_scout, name='add_scout'),
    path('student/<int:student_pk>/remove_scout/', views.remove_scout, name='remove_scout'),
    
    # 教員コメント編集
    path('student/<int:pk>/comment/', views.StudentCommentUpdateView.as_view(), name='student_comment_update'),

    # ★★★ ↓↓ ここを修正しました (StudentProfileUpdateView -> ProfileUpdateView) ↓↓ ★★★
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_update'),
    # ★★★ ↑↑↑ ★★★

    # タグ設定
    path('profile/tags/student/', views.StudentTagUpdateView.as_view(), name='student_tag_update'),
    path('profile/tags/company/', views.CompanyTagUpdateView.as_view(), name='company_tag_update'),
]