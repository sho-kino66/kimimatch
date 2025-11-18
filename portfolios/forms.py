from django import forms
from .models import Portfolio
from .models import Portfolio, PortfolioItem

# models.py で定義した Portfolio モデルを元に、フォームを自動作成
class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio  # 1. 元にするモデルを指定
        
        # 2. フォームに表示する項目を指定
        fields = ['title', 'description'] 
        
        # 3. フォームの表示ラベル（日本語名）を指定
        labels = {
            'title': 'ポートフォリオのタイトル',
            'description': '概要・説明文',
        }

# 2. ↓ PortfolioItemForm を新規追加 ↓
class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem # PortfolioItem モデルを使う
        fields = ['file']     # 'file' フィールドだけをフォームに表示
        labels = {
            'file': 'アップロードするファイル',
        }

class PortfolioCommentForm(forms.ModelForm):
    # ★ 1. フィールドを明示的に定義
    teacher_comment = forms.CharField(
        label="この作品へのコメント",
        max_length=500,  # ← ★ここに文字数制限 (例: 500文字) を設定
        required=False,
        widget=forms.Textarea(attrs={'rows': 5})
    )
    class Meta:
        model = Portfolio # Portfolio モデルを直接編集
        fields = ['teacher_comment'] # このフィールドだけを編集
        labels = {
            'teacher_comment': 'この作品へのコメント',
        }
        widgets = {
            'teacher_comment': forms.Textarea(attrs={'rows': 5}),
        }