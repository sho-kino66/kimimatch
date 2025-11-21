from django.shortcuts import render,redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Company, Scout
# ↓ ステップ1で作成した Mixin をインポート
from accounts.views import StudentOrTeacherOnlyMixin,CompanyOnlyMixin
from accounts.models import FavoriteCompany, Student
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User # 1. User をインポート
from chat.models import ChatRoom           # 2. ChatRoom をインポート
from django.db.models import Count,Q   
     # 3. Count をインポート
from core.utils import calculate_match_percentage     

# 1. 企業一覧ビュー
class CompanyListView(LoginRequiredMixin, StudentOrTeacherOnlyMixin, ListView):
    model = Company
    template_name = 'companies/company_list.html' # 使うテンプレート
    context_object_name = 'companies' # テンプレート内で使う変数名
    paginate_by = 10 

    def get_queryset(self):
        queryset = Company.objects.all()
        
        # 1. 検索 (Search)
        query = self.request.GET.get('query')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(industry__icontains=query) |
                Q(description__icontains=query)|
                #タグ名での検索追加
                Q(tags__tag__name__icontains=query)
            )
        
        # 2. ソート (Sort)
        sort_by = self.request.GET.get('sort')
        
        if sort_by == 'industry':
            queryset = queryset.order_by('industry')
        else:
            # デフォルトのソート（企業名順）
            queryset = queryset.order_by('name')

        # 3. 重複除去と返却
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('query', '')
        context['sort_by'] = self.request.GET.get('sort', 'name')
        return context

# 2. 企業詳細ビュー
class CompanyDetailView(LoginRequiredMixin, StudentOrTeacherOnlyMixin, DetailView):
    model = Company
    template_name = 'companies/company_detail.html'
    context_object_name = 'company'
    
    # ↓ この get_context_data メソッドを丸ごと上書き（差し替え）
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.get_object()
        user = self.request.user
        
        # この企業の担当者 (User) を全員取得
        rep_users = User.objects.filter(companyrepresentative__company=company)
        
        # --- ログインユーザーが「学生」の場合 ---
        if hasattr(user, 'student'):
            student = user.student

            #マッチ度の計算と追加 
            match_rate = calculate_match_percentage(student, company)
            context['match_rate'] = match_rate
            
            # (A) お気に入り状態をチェック
            is_favorited = FavoriteCompany.objects.filter(student=student, company=company).exists()
            context['is_favorited'] = is_favorited
            
            # (B) チャットルームの状態をチェック
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
        
        # --- ↓↓ ここから下を新規追加 ↓↓ ---
        
        # --- ログインユーザーが「教員」の場合 ---
        elif hasattr(user, 'teacher'):
            teacher_user = user # 教員本人 (User)
            
            if rep_users.exists():
                # 企業担当者と教員の既存ルームを探す
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
        # --- ↑↑ ここまで新規追加 ↑↑ ---
            
        return context

# 4. お気に入り追加ビュー
@login_required
def add_favorite(request, company_pk):
    # ログインユーザーが学生でなければ何もしない (簡易チェック)
    if not hasattr(request.user, 'student'):
        return redirect('companies:detail', pk=company_pk)
        
    company = get_object_or_404(Company, pk=company_pk)
    student = request.user.student
    
    # 既にお気に入りしていなければ、作成する
    FavoriteCompany.objects.get_or_create(student=student, company=company)
    
    # 元の企業詳細ページに戻る
    return redirect('companies:detail', pk=company_pk)


# 5. お気に入り削除ビュー
@login_required
def remove_favorite(request, company_pk):
    if not hasattr(request.user, 'student'):
        return redirect('companies:detail', pk=company_pk)
        
    company = get_object_or_404(Company, pk=company_pk)
    student = request.user.student
    
    # お気に入りオブジェクトを探して削除する
    FavoriteCompany.objects.filter(student=student, company=company).delete()
    
    # 元の企業詳細ページに戻る
    return redirect('companies:detail', pk=company_pk)

# スカウト済み学生一覧ビュー
class ScoutedStudentListView(LoginRequiredMixin, CompanyOnlyMixin, ListView):
    model = Scout # 1. ベースとなるモデルはスカウトテーブル
    template_name = 'companies/scouted_student_list.html'
    context_object_name = 'scouts'
    paginate_by = 10

    def get_queryset(self):
        # ログインしている企業担当者の「所属企業」を取得
        company = self.request.user.companyrepresentative.company
        
        # 自分の会社がスカウトした情報（Scout）を、登録が新しい順に取得
        return Scout.objects.filter(company=company).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = self.request.user.companyrepresentative.company.name
        return context