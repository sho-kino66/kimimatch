from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Student
from .models import Student, Teacher, CompanyRepresentative, FavoriteCompany
from companies.models import Company # 企業を選択するためにインポート
from schools.models import School   # 学校を選択するためにインポート
from django.db import transaction
from core.models import Tag
from .models import Student
from companies.models import CompanyTag

#学生用タグ設定フォーム
class StudentTagUpdateForm(forms.Form):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        # ★★★ 修正: カテゴリごとにリストを分ける ★★★
        # 「強み」には、categoryが 'strength' または 'both' のものを表示
        self.strength_tags = Tag.objects.filter(category__in=['strength', 'both'])
        # 「条件」には、categoryが 'condition' または 'both' のものを表示
        self.condition_tags = Tag.objects.filter(category__in=['condition', 'both'])
        
        # 1. 自分の強み (1位〜5位)
        for i in range(1, 6):
            self.fields[f'strength_{i}'] = forms.ModelChoiceField(
                queryset=self.strength_tags,
                label=f'自分の強み {i}位',
                required=False,
                widget=forms.Select(attrs={'class': 'form-control'})
            )
        # 2. 会社に求めるもの (1位〜5位)
        for i in range(1, 6):
            self.fields[f'desire_{i}'] = forms.ModelChoiceField(
                queryset=self.condition_tags,
                label=f'会社に求めるもの {i}位',
                required=False,
                widget=forms.Select(attrs={'class': 'form-control'})
            )

    def save(self):
        student = self.user.student
        # 既存のタグを一度クリア
        StudentTag.objects.filter(student=student).delete()
        
        # フォームの入力値を保存
        for key, value in self.cleaned_data.items():
            if value:
                tag_type, rank_str = key.split('_')
                rank = int(rank_str)
                
                StudentTag.objects.create(
                    student=student,
                    tag=value,
                    tag_type=tag_type,
                    rank=rank
                )

# 企業用タグ設定フォーム
class CompanyTagUpdateForm(forms.Form):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        # ★★★ 修正: カテゴリごとにリストを分ける ★★★
        # 「強み」には、categoryが 'strength' または 'both' のものを表示
        self.strength_tags = Tag.objects.filter(category__in=['strength', 'both'])
        # 「条件」には、categoryが 'condition' または 'both' のものを表示
        self.condition_tags = Tag.objects.filter(category__in=['condition', 'both'])
        
        # 1. 求める人材の強み (1位〜5位)
        for i in range(1, 6):
            self.fields[f'strength_{i}'] = forms.ModelChoiceField(
                queryset=self.strength_tags,
                label=f'求める人材の強み {i}位',
                required=False,
                widget=forms.Select(attrs={'class': 'form-control'})
            )
        # 2. 自社の特徴・政策 (1位〜5位)
        for i in range(1, 6):
            self.fields[f'feature_{i}'] = forms.ModelChoiceField(
                queryset=self.condition_tags,
                label=f'自社の特徴・政策 {i}位',
                required=False,
                widget=forms.Select(attrs={'class': 'form-control'})
            )

    def save(self):
        company = self.user.companyrepresentative.company
        CompanyTag.objects.filter(company=company).delete()
        
        for key, value in self.cleaned_data.items():
            if value:
                tag_type, rank_str = key.split('_')
                rank = int(rank_str)
                
                CompanyTag.objects.create(
                    company=company,
                    tag=value,
                    tag_type=tag_type,
                    rank=rank
                )

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

# 学生プロフィール編集フォーム
class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        # 編集を許可するフィールド
        fields = ['full_name', 'grade', 'school', 'is_public_to_companies']
        labels = {
            'full_name': '氏名',
            'grade': '学年',
            'school': '所属学校',
            'is_public_to_companies': '企業へのプロフィール公開',
        }

# 教員プロフィール編集フォーム
class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['full_name', 'subject', 'school']
        labels = {
            'full_name': '氏名',
            'subject': '担当教科',
            'school': '所属学校',
        }

# 企業担当者プロフィール編集フォーム
class CompanyRepresentativeProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyRepresentative
        fields = ['full_name', 'department']
        labels = {
            'full_name': '担当者氏名',
            'department': '所属部署',
        }