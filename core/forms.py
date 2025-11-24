from django import forms

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
        widget=forms.TextInput(attrs={'class': 'input-full'})
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
        widget=forms.TextInput(attrs={'class': 'input-full'})
    )
    address = forms.CharField(
        label="住所", max_length=255, required=True,
        widget=forms.TextInput(attrs={'class': 'input-full', 'placeholder': '例：東京都新宿区西新宿1-1-1'})
    )