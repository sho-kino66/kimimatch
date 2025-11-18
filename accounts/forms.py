from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Student
from .models import Student, Teacher, CompanyRepresentative
from companies.models import Company # 企業を選択するためにインポート
from schools.models import School   # 学校を選択するためにインポート
from django.db import transaction

# Django標準のUserCreationFormを拡張して、学生プロフィールも同時作成する
class StudentSignUpForm(UserCreationForm):
    # Studentモデルの項目（models.pyで定義したもの）
    full_name = forms.CharField(max_length=100, label="氏名")
    grade = forms.IntegerField(label="学年")
    # school = ... (学校を選ぶ機能は後で追加します)

    class Meta(UserCreationForm.Meta):
        model = User # ログイン用のUserモデル
    
    def save(self, commit=True):
        # 1. ログイン用のUserアカウントを保存
        user = super().save(commit=False)
        
        if commit:
            user.save() # Userをデータベースに保存
            
            # 2. Studentプロフィールを作成・保存
            Student.objects.create(
                user=user, # 今作成したUserと紐付け
                full_name=self.cleaned_data.get('full_name'),
                grade=self.cleaned_data.get('grade'),
            )
        return user

# 2. 教員用サインアップフォーム
class TeacherSignUpForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, label="氏名")
    subject = forms.CharField(max_length=50, label="担当教科")
    
    # 学校を選択
    school = forms.ModelChoiceField(
        queryset=School.objects.all(),
        label="所属学校",
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = User
    
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()
        
        Teacher.objects.create(
            user=user,
            full_name=self.cleaned_data.get('full_name'),
            subject=self.cleaned_data.get('subject'),
            school=self.cleaned_data.get('school')
        )
        return user

# 3. 企業担当者用サインアップフォーム
class CompanyRepresentativeSignUpForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, label="担当者名")
    department = forms.CharField(max_length=100, label="所属部署", required=False)
    
    # 既存の企業リストから選択
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        label="所属企業",
        required=True
    )


    class Meta(UserCreationForm.Meta):
        model = User
    
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()
        
        CompanyRepresentative.objects.create(
            user=user,
            full_name=self.cleaned_data.get('full_name'),
            department=self.cleaned_data.get('department'),
            company=self.cleaned_data.get('company')
        )
        return user

class TeacherCommentForm(forms.ModelForm):
    # ★ 1. フィールドを明示的に定義
    comment = forms.CharField(
        label="学生への推薦コメント・指導状況",
        max_length=500,  # ← ★ここに文字数制限 (例: 500文字) を設定
        required=False,  # (空でもOKな場合)
        widget=forms.Textarea(attrs={'rows': 5}) # Textareaを引き続き使用
    )
    class Meta:
        model = Student  # Student モデルを直接編集
        fields = ['comment'] # 'comment' フィールドだけをフォームに表示
        labels = {
            'comment': '学生への推薦コメント・指導状況',
        }
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 5}), # 入力欄を広げる
        }

class StudentProfileUpdateForm(forms.ModelForm):
    # 学校の選択肢を必須にする
    school = forms.ModelChoiceField(
        queryset=School.objects.all(),
        label="所属学校",
        required=True
    )

    class Meta:
        model = Student
        # 編集させたいフィールドを指定
        fields = [
            'full_name', 
            'grade', 
            'school', 
            'is_public_to_companies'
        ]
        labels = {
            'full_name': '氏名',
            'grade': '学年',
            'is_public_to_companies': '企業にプロフィールを公開する'
        }
        help_texts = {
            'is_public_to_companies': 'チェックを外すと、企業側の学生検索一覧に表示されなくなります。'
        }
        widgets = {
            # チェックボックスを大きく見やすくする (オプション)
            'is_public_to_companies': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }