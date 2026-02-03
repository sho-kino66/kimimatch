from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib.auth.models import User

# モデルのインポート
from .models import Company, Scout
from accounts.models import FavoriteCompany, Student
from chat.models import ChatRoom

# Mixinのインポート
from accounts.views import StudentOrTeacherOnlyMixin, CompanyOnlyMixin

# ユーティリティのインポート
from core.utils import calculate_match_percentage

# 1. 企業一覧ビュー (クラスベースビューを整理)
class CompanyListView(LoginRequiredMixin, StudentOrTeacherOnlyMixin, ListView):
    model = Company
    template_name = 'companies/company_list.html'
    context_object_name = 'companies'
    # ★ 1ページに9件を表示するように修正
    paginate_by = 9 

    def get_queryset(self):
        # 最新の登録順で取得
        # queryset = Company.objects.all().order_by('-created_at')  # 削除
        queryset = Company.objects.all().order_by('-id')
        
        # 1. 検索 (Search)
        query = self.request.GET.get('query')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(industry__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__tag__name__icontains=query)
            )
        
        # 2. ソート (Sort)
        sort_by = self.request.GET.get('sort')
        if sort_by == 'industry':
            queryset = queryset.order_by('industry')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # テンプレートに渡す変数名（companies ではなく page_obj を使うのが一般的ですが、
        # ListView のデフォルトでは companies も page_obj も両方使えます）
        context['query'] = self.request.GET.get('query', '')
        context['sort_by'] = self.request.GET.get('sort', 'name')
        return context


# 2. 企業詳細ビュー (変更なし)
class CompanyDetailView(LoginRequiredMixin, StudentOrTeacherOnlyMixin, DetailView):
    model = Company
    template_name = 'companies/company_detail.html'
    context_object_name = 'company'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.get_object()
        user = self.request.user
        
        rep_users = User.objects.filter(companyrepresentative__company=company)
        
        if hasattr(user, 'student'):
            student = user.student
            match_data = calculate_match_percentage(student, company)
            context['match_rate'] = match_data['percentage']
            context['matched_strengths'] = match_data['matched_strengths']
            context['matched_conditions'] = match_data['matched_conditions']
            
            is_favorited = FavoriteCompany.objects.filter(student=student, company=company).exists()
            context['is_favorited'] = is_favorited
            
            if rep_users.exists():
                existing_room = ChatRoom.objects.annotate(
                    num_participants=Count('participants')
                ).filter(
                    num_participants=2,
                    participants=student.user
                ).filter(
                    participants__in=rep_users
                ).first()

                if existing_room:
                    context['existing_chat_room_id'] = existing_room.id
                else:
                    context['first_rep_user_id'] = rep_users.first().id
        
        elif hasattr(user, 'teacher'):
            teacher_user = user
            if rep_users.exists():
                existing_room = ChatRoom.objects.annotate(
                    num_participants=Count('participants')
                ).filter(
                    num_participants=2,
                    participants=teacher_user
                ).filter(
                    participants__in=rep_users
                ).first()
            
                if existing_room:
                    context['existing_chat_room_id'] = existing_room.id
                else:
                    context['first_rep_user_id'] = rep_users.first().id
            
        return context


# 3. お気に入り追加・削除 (変更なし)
@login_required
def add_favorite(request, company_pk):
    if not hasattr(request.user, 'student'):
        return redirect('companies:company_detail', pk=company_pk)
    company = get_object_or_404(Company, pk=company_pk)
    FavoriteCompany.objects.get_or_create(student=request.user.student, company=company)
    return redirect('companies:company_detail', pk=company_pk)

@login_required
def remove_favorite(request, company_pk):
    if not hasattr(request.user, 'student'):
        return redirect('companies:company_detail', pk=company_pk)
    FavoriteCompany.objects.filter(student=request.user.student, company=company_pk).delete()
    next_url = request.POST.get('next') or request.GET.get('next')
    return redirect(next_url if next_url else f'/companies/detail/{company_pk}/')

# 4. スカウト済み学生一覧
class ScoutedStudentListView(LoginRequiredMixin, CompanyOnlyMixin, ListView):
    model = Scout
    template_name = 'companies/scouted_student_list.html'
    context_object_name = 'scouts'
    paginate_by = 10

    def get_queryset(self):
        if hasattr(self.request.user, 'companyrepresentative'):
            company = self.request.user.companyrepresentative.company
            return Scout.objects.filter(company=company).order_by('-created_at')
        return Scout.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'companyrepresentative'):
            context['company_name'] = self.request.user.companyrepresentative.company.name
        return context