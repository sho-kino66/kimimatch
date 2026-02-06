from django import forms
from .models import Portfolio, PortfolioItem

# 1. ポートフォリオ（表紙・概要）用フォーム
class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['title', 'description'] 
        labels = {
            'title': 'ポートフォリオのタイトル',
            'description': '概要・説明文',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control count-target',
                'placeholder': '30文字以内',
                'data_limit': '30',  # ★ハイフンをアンダースコアに変更
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control count-target',
                'rows': 5,
                'placeholder': '300文字以内',
                'data_limit': '300', # ★ハイフンをアンダースコアに変更
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 前回の修正通り maxlength を削除
        if 'title' in self.fields:
            self.fields['title'].widget.attrs.pop('maxlength', None)
        if 'description' in self.fields:
            self.fields['description'].widget.attrs.pop('maxlength', None)
# 2. ポートフォリオ作品（ファイル）用フォーム
class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ['file']
        labels = {
            'file': 'アップロードするファイル',
        }
        # ファイル選択ボタンにもBootstrap等のクラスを当てる場合はここに追加できます

# 3. 教員用コメントフォーム
class PortfolioCommentForm(forms.ModelForm):
    teacher_comment = forms.CharField(
        label="この作品へのコメント",
        max_length=500, # サーバー側のバリデーション
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 5,
            'class': 'form-control',
            'placeholder': '学生へのアドバイスや評価を記入してください（500文字以内）',
            'maxlength': '500', # ★クライアント側の制限
        })
    )
    class Meta:
        model = Portfolio
        fields = ['teacher_comment']
        labels = {
            'teacher_comment': 'この作品へのコメント',
        }