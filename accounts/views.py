from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Student, Teacher, CompanyRepresentative, FavoriteCompany
from .forms import (StudentSignUpForm, TeacherSignUpForm, CompanyRepresentativeSignUpForm,
                    TeacherCommentForm,
                    StudentProfileUpdateForm )
from django.shortcuts import render, redirect, get_object_or_404
from companies.models import Company, Scout
from chat.models import ChatRoom # ChatRoom もインポート
from django.db.models import Q, Count
from portfolios.models import Portfolio
from core.models import Announcement
from django.core.paginator import Paginator

# ==================================
# 1. 新規登録（サインアップ）関連
# ==================================

# 登録タイプの選択画面
def signup_type_select(request):
    return render(request, 'accounts/signup_type_select.html')

# 学生用の新規登録ビュー
class StudentSignUpView(CreateView):
    form_class = StudentSignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login') # ログイン画面に戻す

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = '学生'
        return context

# 教員用サインアップビュー
class TeacherSignUpView(CreateView):
    form_class = TeacherSignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = '教員'
        return context

# 企業担当者用サインアップビュー
class CompanyRepresentativeSignUpView(CreateView):
    form_class = CompanyRepresentativeSignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = '企業担当者'
        return context

# ==================================
# 2. 権限チェック用 Mixin (クラス)
# ==================================

# --- 【修正点】不足していた StudentOnlyMixin をここに追加  ---
class StudentOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        try:
            return hasattr(self.request.user, 'student')
        except:
            return False

# --- 教員専用 ---
class TeacherOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        try:
            return hasattr(self.request.user, 'teacher')
        except:
            return False

# --- 教員または企業担当者 ---
class TeacherOrCompanyOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        try:
            return (
                hasattr(self.request.user, 'teacher') or 
                hasattr(self.request.user, 'companyrepresentative') or
                self.request.user.is_superuser
            )
        except:
            return False

# --- 企業担当者専用 ---
class CompanyOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        try:
            return hasattr(self.request.user, 'companyrepresentative')
        except:
            return False

# --- 学生または教員専用 ---
class StudentOrTeacherOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        try:
            return (
                hasattr(self.request.user, 'student') or
                hasattr(self.request.user, 'teacher')
            )
        except:
            return False

# ==================================
# 3. 共通ビュー (ダッシュボード・マイページ)
# ==================================
@login_required
def dashboard(request):
    user = request.user
    user_type = None
    profile = None
    
    # --- ユーザー種別とプロフィールの判定 (既存のコード) ---
    try:
        profile = user.student
        user_type = 'student'
    except Student.DoesNotExist:
        try:
            profile = user.teacher
            user_type = 'teacher'
        except Teacher.DoesNotExist:
            try:
                profile = user.companyrepresentative
                user_type = 'company'
            except CompanyRepresentative.DoesNotExist:
                if user.is_superuser:
                    user_type = 'admin'
                else:
                    user_type = 'unassigned' 
    
    # --- ↓↓ 変更部分: ページネーションの実装 ↓↓ ---
    
    # 1. 全てのお知らせを取得
    announcement_list = Announcement.objects.all().order_by('-created_at')
    
    # 2. Paginatorを設定 (1ページあたり5件)
    paginator = Paginator(announcement_list, 5)
    
    # 3. URLのパラメータ(?page=2など)から現在のページ番号を取得
    page_number = request.GET.get('page')
    
    # 4. 指定されたページのデータ（page_obj）を取得
    page_obj = paginator.get_page(page_number)

    context = {
        'username': user.username,
        'user_type': user_type,
        'profile': profile,
        # テンプレートには page_obj を 'announcements' として渡します
        'announcements': page_obj, 
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def my_page(request):
    user = request.user
    user_type = None
    profile = None
    template_name = 'accounts/my_page.html'
    
    # --- ★【修正点】ロジックを dashboard と統一 ---
    try:
        profile = user.student
        user_type = 'student'
        # 学生のポートフォリオ一覧を取得（新しい順）
        portfolios = profile.portfolio_set.all().order_by('-id')
    except Student.DoesNotExist:
        try:
            profile = user.teacher
            user_type = 'teacher'
        except Teacher.DoesNotExist:
            try:
                profile = user.companyrepresentative
                user_type = 'company'
            except CompanyRepresentative.DoesNotExist:
                if user.is_superuser:
                    return redirect('admin:index')
                else:
                    user_type = 'unassigned'
                    
    if user.is_superuser and not profile:
         return redirect('admin:index')
         
    context = {
        'user_type': user_type,
        'profile': profile,
    }
    if user_type == 'student':
        # 学生の場合のみ、コンテキストにポートフォリオリストを追加
        context['portfolios'] = portfolios
    return render(request, template_name, context)

# ==================================
# 4. 閲覧ビュー (一覧・詳細)
# ==================================

# 担当学生一覧ビュー (教員用)
class TeacherStudentListView(LoginRequiredMixin, TeacherOnlyMixin, ListView):
    model = Student
    template_name = 'accounts/teacher_student_list.html'
    context_object_name = 'students'

    def get_queryset(self):
        teacher = self.request.user.teacher
        queryset = Student.objects.filter(school=teacher.school)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['school_name'] = self.request.user.teacher.school.name
        return context

# 学生詳細ビュー (教員・企業用)
class StudentDetailView(LoginRequiredMixin, TeacherOrCompanyOnlyMixin, DetailView):
    model = Student
    template_name = 'accounts/student_detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        user = self.request.user # ログイン中のユーザー
        
        # 1. 学生のポートフォリオ一覧を取得
        context['portfolios'] = student.portfolio_set.all()
        
        # 2. ログインユーザーが企業担当者の場合
        if hasattr(user, 'companyrepresentative'):
            company = user.companyrepresentative.company
            
            # (A) スカウト状態をチェック (既存のロジック)
            is_scouted = Scout.objects.filter(company=company, student=student).exists()
            context['is_scouted'] = is_scouted
            
            # (B) この学生の学校に所属する教員一覧を取得
            if student.school:
                teachers = Teacher.objects.filter(school=student.school)
                context['school_teachers'] = teachers
            
            # (C) 既存のチャットルームIDを取得（学生本人とのチャット）
            
            # --- ↓↓ ここを修正しました (バグ修正) ↓↓ ---
            existing_room = ChatRoom.objects.annotate(
                num_participants=Count('participants')
            ).filter(
                num_participants=2,
                participants=user     # 1. 自分が参加していて
            ).filter(
                participants=student.user # 2. 「かつ」学生も参加している
            ).first()
            # --- ↑↑ ここまで修正 ↑↑ ---
            
            if existing_room:
                context['student_chat_room_id'] = existing_room.id
                
        return context

# 学生一覧ビュー (企業用)
class CompanyStudentListView(LoginRequiredMixin, CompanyOnlyMixin, ListView):
    model = Student
    template_name = 'accounts/company_student_list.html'
    context_object_name = 'students'
    paginate_by = 10 

    def get_queryset(self):
        # Student.objects.all() から、公開OKの学生のみを対象にする
        queryset = Student.objects.filter(is_public_to_companies=True)
        query = self.request.GET.get('query')
        
        if query:
            # 4. 'query' があれば、氏名 or 学校名 で絞り込む
            #    ( distinct() は、ポートフォリオ検索などで重複した学生を除外するため)
            queryset = queryset.filter(
                Q(full_name__icontains=query) |
                Q(school__name__icontains=query) |
                Q(portfolio__title__icontains=query) |
                Q(portfolio__description__icontains=query)
            ).distinct()
            
        # --- ↑ ここまで追記 ↑ ---
            
        return queryset

    # --- ↓ get_context_data を追記（検索キーワードをテンプレートに戻すため）↓ ---
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # テンプレートに、現在検索中のキーワードを渡す
        context['query'] = self.request.GET.get('query', '') 
        return context

# お気に入り企業一覧ビュー (学生用)
class FavoriteCompanyListView(LoginRequiredMixin, StudentOnlyMixin, ListView):
    model = FavoriteCompany
    template_name = 'accounts/favorite_company_list.html'
    context_object_name = 'favorites'
    paginate_by = 10

    def get_queryset(self):
        student = self.request.user.student
        return FavoriteCompany.objects.filter(student=student).order_by('-created_at')

# 4. スカウト追加ビュー
@login_required
def add_scout(request, student_pk):
    # ログインユーザーが企業担当者でなければ何もしない
    if not hasattr(request.user, 'companyrepresentative'):
        return redirect('accounts:student_detail', pk=student_pk)
        
    student = get_object_or_404(Student, pk=student_pk)
    company = request.user.companyrepresentative.company # ログイン中の担当者の所属企業
    
    # 既にスカウトしていなければ、作成する
    Scout.objects.get_or_create(company=company, student=student)
    
    # 元の学生詳細ページに戻る
    return redirect('accounts:student_detail', pk=student_pk)


# 5. スカウト削除ビュー
@login_required
def remove_scout(request, student_pk):
    if not hasattr(request.user, 'companyrepresentative'):
        return redirect('accounts:student_detail', pk=student_pk)
        
    student = get_object_or_404(Student, pk=student_pk)
    company = request.user.companyrepresentative.company
    
    # スカウトオブジェクトを探して削除する
    Scout.objects.filter(company=company, student=student).delete()
    
    # フォームから 'next' パラメータ（戻り先のURL）を取得
    next_url = request.POST.get('next')
    
    if next_url:
        # 'next' パラメータがあれば、そこ（スカウト一覧）にリダイレクト
        return redirect(next_url)
    else:
        # なければ、デフォルト（学生詳細ページ）に戻る
        return redirect('accounts:student_detail', pk=student_pk)
    
# 教員による学生コメント編集ビュー
class StudentCommentUpdateView(LoginRequiredMixin, TeacherOnlyMixin, UpdateView):
    model = Student
    form_class = TeacherCommentForm
    template_name = 'accounts/student_comment_form.html' # 使うテンプレート
    context_object_name = 'student' # テンプレート内で 'student' という名前で使う
    
    def get_queryset(self):
        # 自分が所属する学校の学生のコメントのみ編集可能にする
        teacher = self.request.user.teacher
        return Student.objects.filter(school=teacher.school)

    def form_valid(self, form):
        # フォームが保存される直前に、誰が編集したかを記録
        form.instance.comment_teacher = self.request.user.teacher
        return super().form_valid(form)

    def get_success_url(self):
        # 成功したら、その学生の詳細ページに戻る
        # (self.object は編集された Student インスタンスです)
        student_pk = self.object.pk
        return reverse_lazy('accounts:student_detail', kwargs={'pk': student_pk})

# 学生によるプロフィール編集ビュー
class StudentProfileUpdateView(LoginRequiredMixin, StudentOnlyMixin, UpdateView):
    model = Student
    form_class = StudentProfileUpdateForm
    template_name = 'accounts/student_profile_form.html' # 新しいテンプレート
    success_url = reverse_lazy('accounts:my_page') # 成功したらマイページに戻る

    def get_object(self, queryset=None):
        # URLからPK(ID)を取得するのではなく、
        # ログインしているユーザーの学生プロフィールを編集対象にする
        return self.request.user.student

    def get_context_data(self, **kwargs):
        # テンプレートにタイトルを渡す
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'プロフィール編集'
        return context