from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Student, Teacher, CompanyRepresentative, FavoriteCompany
from .forms import (
    StudentSignUpForm, TeacherSignUpForm, CompanyRepresentativeSignUpForm,
    TeacherCommentForm,
    # ★ StudentProfileUpdateForm は不要になったので削除し、新しく3つのフォームを追加
    StudentProfileForm, TeacherProfileForm, CompanyRepresentativeProfileForm,
    StudentTagUpdateForm, CompanyTagUpdateForm 
)
from companies.models import Company, Scout
from chat.models import ChatRoom
from django.db.models import Q, Count
from portfolios.models import Portfolio
from core.models import Announcement
from django.core.paginator import Paginator
from core.utils import calculate_match_percentage

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
    success_url = reverse_lazy('accounts:login')

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

class StudentOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        try:
            return hasattr(self.request.user, 'student')
        except:
            return False

class TeacherOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        try:
            return hasattr(self.request.user, 'teacher')
        except:
            return False

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

class CompanyOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        try:
            return hasattr(self.request.user, 'companyrepresentative')
        except:
            return False

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
    
    announcement_list = Announcement.objects.all().order_by('-created_at')
    paginator = Paginator(announcement_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'username': user.username,
        'user_type': user_type,
        'profile': profile,
        'announcements': page_obj, 
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def my_page(request):
    user = request.user
    user_type = None
    profile = None
    template_name = 'accounts/my_page.html'
    portfolios = None
    
    try:
        profile = user.student
        user_type = 'student'
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
        context['portfolios'] = portfolios
    return render(request, template_name, context)

# ==================================
# 4. 閲覧・操作ビュー
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
        user = self.request.user
        
        context['portfolios'] = student.portfolio_set.all()
        
        if hasattr(user, 'companyrepresentative'):
            company = user.companyrepresentative.company
            
            is_scouted = Scout.objects.filter(company=company, student=student).exists()
            context['is_scouted'] = is_scouted
            
            if student.school:
                teachers = Teacher.objects.filter(school=student.school)
                context['school_teachers'] = teachers
            
            existing_room = ChatRoom.objects.annotate(
                num_participants=Count('participants')
            ).filter(
                num_participants=2,
                participants=user
            ).filter(
                participants=student.user
            ).first()
            
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
        queryset = Student.objects.filter(is_public_to_companies=True)
        query = self.request.GET.get('query')
        
        if query:
            queryset = queryset.filter(
                Q(full_name__icontains=query) |
                Q(school__name__icontains=query) |
                Q(portfolio__title__icontains=query) |
                Q(portfolio__description__icontains=query)
            ).distinct()
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

# スカウト追加ビュー
@login_required
def add_scout(request, student_pk):
    if not hasattr(request.user, 'companyrepresentative'):
        return redirect('accounts:student_detail', pk=student_pk)
        
    student = get_object_or_404(Student, pk=student_pk)
    company = request.user.companyrepresentative.company
    Scout.objects.get_or_create(company=company, student=student)
    return redirect('accounts:student_detail', pk=student_pk)

# スカウト削除ビュー
@login_required
def remove_scout(request, student_pk):
    if not hasattr(request.user, 'companyrepresentative'):
        return redirect('accounts:student_detail', pk=student_pk)
        
    student = get_object_or_404(Student, pk=student_pk)
    company = request.user.companyrepresentative.company
    Scout.objects.filter(company=company, student=student).delete()
    
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    else:
        return redirect('accounts:student_detail', pk=student_pk)
    
# 教員による学生コメント編集ビュー
class StudentCommentUpdateView(LoginRequiredMixin, TeacherOnlyMixin, UpdateView):
    model = Student
    form_class = TeacherCommentForm
    template_name = 'accounts/student_comment_form.html'
    context_object_name = 'student'
    
    def get_queryset(self):
        teacher = self.request.user.teacher
        return Student.objects.filter(school=teacher.school)

    def form_valid(self, form):
        form.instance.comment_teacher = self.request.user.teacher
        return super().form_valid(form)

    def get_success_url(self):
        student_pk = self.object.pk
        return reverse_lazy('accounts:student_detail', kwargs={'pk': student_pk})


# ★★★ プロフィール編集ビュー (全ユーザー対応版) ★★★
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy('accounts:my_page')

    def get_object(self, queryset=None):
        user = self.request.user
        if hasattr(user, 'student'):
            return user.student
        elif hasattr(user, 'teacher'):
            return user.teacher
        elif hasattr(user, 'companyrepresentative'):
            return user.companyrepresentative
        return None 

    def get_form_class(self):
        user = self.request.user
        if hasattr(user, 'student'):
            return StudentProfileForm
        elif hasattr(user, 'teacher'):
            return TeacherProfileForm
        elif hasattr(user, 'companyrepresentative'):
            return CompanyRepresentativeProfileForm
        return None 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if hasattr(user, 'student'):
            context['user_type_jp'] = '学生'
        elif hasattr(user, 'teacher'):
            context['user_type_jp'] = '教員'
        elif hasattr(user, 'companyrepresentative'):
            context['user_type_jp'] = '企業担当者'
        return context
# ★★★ ↑↑↑ ここまで修正 ↑↑↑ ★★★


# 学生タグ設定ビュー
class StudentTagUpdateView(LoginRequiredMixin, StudentOnlyMixin, FormView):
    template_name = 'accounts/student_tag_form.html'
    form_class = StudentTagUpdateForm
    success_url = reverse_lazy('accounts:my_page')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = {}
        student = self.request.user.student
        for st_tag in student.tags.all():
            key = f"{st_tag.tag_type}_{st_tag.rank}"
            initial[key] = st_tag.tag
        return initial

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

# 企業タグ設定ビュー
class CompanyTagUpdateView(LoginRequiredMixin, CompanyOnlyMixin, FormView):
    template_name = 'accounts/company_tag_form.html'
    form_class = CompanyTagUpdateForm
    success_url = reverse_lazy('accounts:my_page')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = {}
        company = self.request.user.companyrepresentative.company
        for co_tag in company.tags.all():
            key = f"{co_tag.tag_type}_{co_tag.rank}"
            initial[key] = co_tag.tag
        return initial

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)