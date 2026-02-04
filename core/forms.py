from django import forms
from .models import Inquiry
from django.core.validators import RegexValidator  # ★追加

# --- 電話番号用のバリデーター（数字とハイフンのみ許可） ---
tel_validator = RegexValidator(
    regex=r'^[0-9-]+$',
    message='電話番号は数字とハイフン（-）のみで入力してください。'
)

class SchoolApplicationForm(forms.Form):
    school_name = forms.CharField(
        label="学校名", max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'input-full', 'placeholder': '例：〇〇専門学校'})
    )
    contact_name = forms.CharField(
        label="担当者名", max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'input-full'})
    )
    email = forms.EmailField(
        label="メールアドレス", required=True,
        widget=forms.EmailInput(attrs={'class': 'input-full'})
    )
    phone = forms.CharField(
        label="電話番号", max_length=20, required=True,
        validators=[tel_validator],  # ★バリデーターを適用
        widget=forms.TextInput(attrs={'class': 'input-full', 'placeholder': '090-1234-5678', 'type': 'tel'}) # type="tel"を追加
    )
    address = forms.CharField(
        label="住所", max_length=255, required=True,
        widget=forms.TextInput(attrs={'class': 'input-full', 'placeholder': '例：東京都新宿区西新宿1-1-1'})
    )

class CompanyApplicationForm(forms.Form):
    company_name = forms.CharField(
        label="企業名", max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'input-full', 'placeholder': '例：〇〇株式会社'})
    )
    contact_name = forms.CharField(
        label="担当者名", max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'input-full'})
    )
    email = forms.EmailField(
        label="メールアドレス", required=True,
        widget=forms.EmailInput(attrs={'class': 'input-full'})
    )
    phone = forms.CharField(
        label="電話番号", max_length=20, required=True,
        validators=[tel_validator],  # ★バリデーターを適用
        widget=forms.TextInput(attrs={'class': 'input-full', 'placeholder': '03-1234-5678', 'type': 'tel'}) # type="tel"を追加
    )
    address = forms.CharField(
        label="住所", max_length=255, required=True,
        widget=forms.TextInput(attrs={'class': 'input-full', 'placeholder': '例：東京都新宿区西新宿1-1-1'})
    )

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '田中 太郎'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.com'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'スカウト機能について'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'こちらにお問い合わせ内容をご記入ください'}),
        }