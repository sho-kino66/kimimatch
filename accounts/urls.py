from django.urls import path,include
from . import views  # views.py をインポート

app_name = 'accounts'
# ↓ この変数が必須です
urlpatterns = [
    # これから 'accounts/' 関連のURLをここに追加していきます
    # ↓ これを追記 ↓
    # 'accounts/' で始まるURLに、Djangoの認証URLをまとめて追加
    # (login/, logout/, password_change/ などが自動で設定される)
    path('', include('django.contrib.auth.urls')),
    # 登録タイプ選択画面
    path('signup/', views.signup_type_select, name='signup_type_select'),
    # 学生登録画面
    path('signup/student/', views.StudentSignUpView.as_view(), name='signup_student'),
    path('signup/teacher/', views.TeacherSignUpView.as_view(), name='signup_teacher'),
    path('signup/company/', views.CompanyRepresentativeSignUpView.as_view(), name='signup_company'),
    # メインメニュー（ダッシュボード）
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my_page/', views.my_page, name='my_page'),
    path('teacher/student_list/', views.TeacherStudentListView.as_view(), name='teacher_student_list'),
    # <int:pk> は、表示したい学生のID（主キー）を指します
    path('student/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('company/student_list/', views.CompanyStudentListView.as_view(), name='company_student_list'),
    path('favorites/', views.FavoriteCompanyListView.as_view(), name='favorite_list'),
    path('student/<int:student_pk>/add_scout/', views.add_scout, name='add_scout'),
    path('student/<int:student_pk>/remove_scout/', views.remove_scout, name='remove_scout'),
    # <int:pk> は「コメントを編集したい学生(Student)のID」
    path('student/<int:pk>/comment/', views.StudentCommentUpdateView.as_view(), name='student_comment_update'),
    path('profile/edit/', views.StudentProfileUpdateView.as_view(), name='profile_update'),
    path('profile/tags/student/', views.StudentTagUpdateView.as_view(), name='student_tag_update'),
    path('profile/tags/company/', views.CompanyTagUpdateView.as_view(), name='company_tag_update'),
]
