from django import forms
from .models import Inquiry, SchoolApplication, CompanyApplication
from django.core.validators import RegexValidator

# --- 電話番号用のバリデーター ---
tel_validator = RegexValidator(
    regex=r'^[0-9-]+$',
    message='電話番号は数字とハイフン（-）のみで入力してください。'
)

# --- 学校申し込みフォーム ---
class SchoolApplicationForm(forms.ModelForm):
    class Meta:
        model = SchoolApplication
        fields = ['school_name', 'contact_name', 'email', 'phone', 'address']
        widgets = {
            'school_name': forms.TextInput(attrs={'class': 'input-full', 'placeholder': '例：〇〇専門学校'}),
            'contact_name': forms.TextInput(attrs={'class': 'input-full'}),
            'email': forms.EmailInput(attrs={'class': 'input-full'}),
            'phone': forms.TextInput(attrs={'class': 'input-full', 'placeholder': '090-1234-5678', 'type': 'tel'}),
            'address': forms.TextInput(attrs={'class': 'input-full', 'placeholder': '例：東京都新宿区西新宿1-1-1'}),
        }

    # ラベルを日本語にするために個別に定義（ModelForm内）
    school_name = forms.CharField(label="学校名")
    contact_name = forms.CharField(label="担当者名")
    email = forms.EmailField(label="メールアドレス")
    phone = forms.CharField(label="電話番号", validators=[tel_validator])
    address = forms.CharField(label="住所")

# --- 企業申し込みフォーム ---
class CompanyApplicationForm(forms.ModelForm):
    class Meta:
        model = CompanyApplication
        fields = ['company_name', 'contact_name', 'email', 'phone', 'address']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'input-full', 'placeholder': '例：〇〇株式会社'}),
            'contact_name': forms.TextInput(attrs={'class': 'input-full'}),
            'email': forms.EmailInput(attrs={'class': 'input-full'}),
            'phone': forms.TextInput(attrs={'class': 'input-full', 'placeholder': '03-1234-5678', 'type': 'tel'}),
            'address': forms.TextInput(attrs={'class': 'input-full', 'placeholder': '例：東京都新宿区西新宿1-1-1'}),
        }

    company_name = forms.CharField(label="企業名")
    contact_name = forms.CharField(label="担当者名")
    email = forms.EmailField(label="メールアドレス")
    phone = forms.CharField(label="電話番号", validators=[tel_validator])
    address = forms.CharField(label="住所")

# --- お問い合わせフォーム ---
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