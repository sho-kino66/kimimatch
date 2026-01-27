import re
import requests
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView, ListView, DetailView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .models import Portfolio, PortfolioItem
from .forms import PortfolioForm, PortfolioItemForm, PortfolioCommentForm # 1. フォームをインポート
# 2. accounts アプリから TeacherOnlyMixin と Student をインポート
from accounts.views import TeacherOnlyMixin 
from accounts.models import Student

# --- 権限チェック用のMixin (PortfolioItem 用) ---
class PortfolioItemOwnerOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        # 今開こうとしている「作品ファイル (Item)」を取得
        item = self.get_object()
        # ログイン中の学生のプロフィールと、
        # その作品が属するポートフォリオの持ち主が一致するか確認
        try:
            return item.portfolio.student == self.request.user.student
        except Student.DoesNotExist:
            return False
# --- 権限チェック用のMixin ---
# (自分が作成した学生かどうかをチェックする)
class StudentOwnerOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        # 今開こうとしているポートフォリオを取得
        portfolio = self.get_object()
        # ログイン中の学生のプロフィールと、ポートフォリオの持ち主が一致するか確認
        try:
            return portfolio.student == self.request.user.student
        except Student.DoesNotExist:
            return False

# 2. ポートフォリオを新規作成するビュー
class PortfolioCreateView(LoginRequiredMixin, CreateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'portfolios/portfolio_form.html' # 使うテンプレート
    success_url = reverse_lazy('accounts:my_page')
    
    def get_success_url(self):
        """
        フォーム保存成功後のリダイレクト先を動的に決定する
        self.object には、今作成された Portfolio インスタンスが格納されている
        """
        # 今作成したポートフォリオの詳細ページ (portfolios:detail) のURLを返す
        return reverse('portfolios:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        # フォームが送信される直前に、誰が作成したかを自動でセットする
        try:
            student = self.request.user.student
            form.instance.student = student
            return super().form_valid(form)
        except Student.DoesNotExist:
            # もし学生プロフィールがないユーザー（教員など）が
            # 直接URLを叩いた場合の安全対策
            form.add_error(None, '学生としてログインしていません。')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        # テンプレートに「作成」というタイトルを渡す
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'ポートフォリオの新規作成'
        return context
    
# 6. PortfolioDetailView を修正 (get_context_data を追加)
class PortfolioDetailView(LoginRequiredMixin, StudentOwnerOnlyMixin, DetailView):
    model = Portfolio
    template_name = 'portfolios/portfolio_detail.html'
    context_object_name = 'portfolio'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        portfolio = self.get_object()
        
        # 既存の作品アイテム一覧を取得してテンプレートに渡す
        context['items'] = portfolio.items.all()
        
        # 新規アップロード用の空のフォームをテンプレートに渡す
        context['item_form'] = PortfolioItemForm()
        
        return context

# 4. ポートフォリオ編集ビュー
class PortfolioUpdateView(LoginRequiredMixin, StudentOwnerOnlyMixin, UpdateView):
    model = Portfolio
    form_class = PortfolioForm # 4-9で作成したフォームを再利用
    template_name = 'portfolios/portfolio_form.html' # 作成画面のテンプレートを再利用
    
    def get_success_url(self):
        # フォームから 'next' パラメータ（戻り先のURL）を取得
        next_url = self.request.POST.get('next')
        
        if next_url:
            # 'next' があれば、そこ（マイページ or 作品管理）に戻る
            return next_url
        else:
            # 'next' が指定されなかった場合のデフォルト（安全策としてマイページ）
            return reverse_lazy('accounts:my_page')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'ポートフォリオの編集' # テンプレートに渡すタイトル
        return context

# 5. ポートフォリオ削除ビュー
class PortfolioDeleteView(LoginRequiredMixin, StudentOwnerOnlyMixin, DeleteView):
    model = Portfolio
    template_name = 'portfolios/portfolio_confirm_delete.html'
    success_url = reverse_lazy('accounts:my_page')

# 7. ↓ ファイルアップロード処理用のビューを新規追加 ↓
@login_required
def add_portfolio_item(request, portfolio_pk):
    portfolio = get_object_or_404(Portfolio, pk=portfolio_pk)
    
    # セキュリティチェック：持ち主か確認
    try:
        if portfolio.student != request.user.student:
            return HttpResponseForbidden("アクセス権がありません。")
    except Student.DoesNotExist:
        return HttpResponseForbidden("アクセス権がありません。")

    # POSTリクエスト（＝フォームが送信された）の場合のみ処理
    if request.method == 'POST':
        form = PortfolioItemForm(request.POST, request.FILES) # 8. request.FILES が重要！
        if form.is_valid():
            item = form.save(commit=False)
            item.portfolio = portfolio # どのポートフォリオに紐付くか設定
            item.save()
            
    # 処理が終わったら、元の詳細ページにリダイレクトする
    return redirect('portfolios:detail', pk=portfolio_pk)

# ↓ ファイル削除用のビューを新規追加 ↓
class PortfolioItemDeleteView(LoginRequiredMixin, PortfolioItemOwnerOnlyMixin, DeleteView):
    model = PortfolioItem
    template_name = 'portfolios/portfolio_item_confirm_delete.html'
    context_object_name = 'item' # テンプレート内で 'item' という名前で使う

    def get_success_url(self):
        # 削除が成功したら、そのアイテムが属していたポートフォリオの詳細ページに戻る
        portfolio = self.object.portfolio
        return reverse_lazy('portfolios:detail', kwargs={'pk': portfolio.pk})

# ポートフォリオへの教員コメント編集ビュー
class PortfolioCommentUpdateView(LoginRequiredMixin, TeacherOnlyMixin, UpdateView):
    model = Portfolio
    form_class = PortfolioCommentForm
    template_name = 'portfolios/portfolio_comment_form.html' # 使うテンプレート
    context_object_name = 'portfolio'
    
    def get_queryset(self):
        # 自分が所属する学校の学生のポートフォリオのみ編集可能にする
        teacher = self.request.user.teacher
        # student__school で、Portfolio -> Student -> School と辿る
        return Portfolio.objects.filter(student__school=teacher.school)

    def form_valid(self, form):
        # フォームが保存される直前に、誰が編集したかを記録
        form.instance.commenting_teacher = self.request.user.teacher
        return super().form_valid(form)

    def get_success_url(self):
        # 成功したら、その学生の詳細ページに戻る
        # (self.object は編集された Portfolio インスタンス)
        student_pk = self.object.student.pk
        return reverse_lazy('accounts:student_detail', kwargs={'pk': student_pk})

# portfolios/views.py

# --- 共通のAI採点処理（関数として独立させる） ---
def _run_ai_grading(item):
    import re, requests
    
    uploaded_file = item.file 
    external_ai_url = "[https://overtrustfully-pinnatisect-jarod.ngrok-free.dev/grade_file/](https://overtrustfully-pinnatisect-jarod.ngrok-free.dev/grade_file/)"
    headers = {"ngrok-skip-browser-warning": "true", "User-Agent": "Django-Client"}

    try:
        with uploaded_file.open('rb') as f:
            files = {'upload': (uploaded_file.name, f.read(), 'application/octet-stream')}
            response = requests.post(external_ai_url, files=files, headers=headers, timeout=180, verify=False)
        
        if response.status_code == 200:
            ai_data = response.json()
            raw_text = ai_data.get('result', '')

            # --- 1. スコア抽出：複数ファイルがあっても確実に拾う ---
            def extract_score_robust(keywords, text):
                # まず、全体から「キーワード: 数字/25」の形を優先して探す
                for key in keywords:
                    pattern = fr'{key}[^0-9\n]*?(\d+)\s*/\s*25'
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        return int(match.group(1))
                
                # 見つからない場合はセクション分割で探す
                sections = re.split(r'#+', text)
                for section in sections:
                    if any(key in section for key in keywords):
                        match = re.search(r'(\d+)', section)
                        if match:
                            return min(int(match.group(1)), 25)
                return 0

            s1 = extract_score_robust(["正確性", "准确性", "Accuracy"], raw_text)
            s2 = extract_score_robust(["可読性", "Readability", "読みやすさ"], raw_text)
            s3 = extract_score_robust(["パフォーマンス", "性能", "Performance"], raw_text)
            s4 = extract_score_robust(["スタイル", "飾り", "Style", "規約"], raw_text)
            
            total_score = s1 + s2 + s3 + s4

            # --- 2. フィードバックのクリーニング：ZIP対応の安全な切り出し ---
            # システムタグの除去
            clean_text = re.sub(r'\[+SCORE\]+|\[+END\]+', '', raw_text).strip()
            
            # 【重要】以前の「```python」での一律カットを廃止
            # 代わりに、明らかに「ソースコード一式の転記」が始まる目印だけを探す
            cutoff_markers = [
                r'【採点対象コード】',
                r'## 採点対象ソースコード',
                r'## ソースコード全文',
                r'以下は採点対象のソースコードです'
            ]
            
            for marker in cutoff_markers:
                parts = re.split(marker, clean_text)
                if len(parts) > 1:
                    clean_text = parts[0]
                    break
            
            # --- 3. 最終チェック：詳細が短すぎないか ---
            # もしクリーニングの結果が短すぎたら、安全策として全文（タグ抜き）を採用
            if len(clean_text) < 50:
                clean_text = re.sub(r'\[+SCORE\]+|\[+END\]+', '', raw_text).strip()

            # 保存
            item.ai_score = total_score
            item.ai_feedback = clean_text.strip()
            item.save()
            return True
            
    except Exception as e:
        print(f"AI Grading Error: {e}")
        
    return False

# アップロード処理を修正
@login_required
def add_portfolio_item(request, portfolio_pk):
    portfolio = get_object_or_404(Portfolio, pk=portfolio_pk)
    if request.method == 'POST':
        form = PortfolioItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.portfolio = portfolio
            item.save()
            
            # ★ 作成したばかりの「item」を採点に回す
            _run_ai_grading(item)
            
    return redirect('portfolios:detail', pk=portfolio_pk)

# --- 個別採点ボタン用（再採点したい時のために残す） ---
@csrf_exempt
@login_required
def grade_portfolio_ai(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk)
    if _run_ai_grading(portfolio):
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'error': '採点に失敗しました'})

class PortfolioItemDeleteView(LoginRequiredMixin, PortfolioItemOwnerOnlyMixin, DeleteView):
    model = PortfolioItem
    template_name = 'portfolios/portfolio_item_confirm_delete.html'
    context_object_name = 'item'

    def get_success_url(self):
        portfolio = self.object.portfolio
        
        # アイテム（ファイル）を削除した後、他にアイテムが1つも残っていなければAI結果を消す
        if portfolio.items.count() == 1: # 削除される「前」のカウントなので 1 の時にリセット
            portfolio.ai_score = None
            portfolio.ai_feedback = None
            portfolio.save()
            
        return reverse_lazy('portfolios:detail', kwargs={'pk': portfolio.pk})