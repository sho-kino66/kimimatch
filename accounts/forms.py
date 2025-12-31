from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError  # 追加: エラー処理用
from django.db import transaction

from companies.models import Company, CompanyTag
from schools.models import School
from core.models import Tag
from .models import Student, Teacher, CompanyRepresentative, FavoriteCompany, StudentTag

# ---------------------------------------------------------
# 学生用タグ設定フォーム (変更なし)
# ---------------------------------------------------------
class StudentTagUpdateForm(forms.Form):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.strength_tags = Tag.objects.filter(category__in=['strength', 'both'])
        self.condition_tags = Tag.objects.filter(category__in=['condition', 'both'])
        
        for i in range(1, 6):
            self.fields[f'strength_{i}'] = forms.ModelChoiceField(
                queryset=self.strength_tags,
                label=f'自分の強み {i}位',
                required=False,
                widget=forms.Select(attrs={'class': 'form-control'})
            )
        for i in range(1, 6):
            self.fields[f'desire_{i}'] = forms.ModelChoiceField(
                queryset=self.condition_tags,
                label=f'会社に求めるもの {i}位',
                required=False,
                widget=forms.Select(attrs={'class': 'form-control'})
            )

    def save(self):
        student = self.user.student
        StudentTag.objects.filter(student=student).delete()
        for key, value in self.cleaned_data.items():
            if value:
                tag_type, rank_str = key.split('_')
                rank = int(rank_str)
                StudentTag.objects.create(
                    student=student, tag=value, tag_type=tag_type, rank=rank
                )

# ---------------------------------------------------------
# 企業用タグ設定フォーム (変更なし)
# ---------------------------------------------------------
class CompanyTagUpdateForm(forms.Form):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.strength_tags = Tag.objects.filter(category__in=['strength', 'both'])
        self.condition_tags = Tag.objects.filter(category__in=['condition', 'both'])
        
        for i in range(1, 6):
            self.fields[f'strength_{i}'] = forms.ModelChoiceField(
                queryset=self.strength_tags,
                label=f'求める人材の強み {i}位',
                required=False,
                widget=forms.Select(attrs={'class': 'form-control'})
            )
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
                    company=company, tag=value, tag_type=tag_type, rank=rank
                )

# ---------------------------------------------------------
# 1. 学生用サインアップフォーム (★修正: 学校コード対応)
# ---------------------------------------------------------
class StudentSignUpForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, label="氏名")
    
    # ★ 変更: IntegerField から ChoiceField に変更し、モデルの選択肢を読み込む
    grade = forms.ChoiceField(
        choices=Student.GRADE_CHOICES, 
        label="学年",
        widget=forms.Select(attrs={'class': 'form-select'}) # Bootstrap用のクラス
    )
    
    school_code = forms.CharField(
        max_length=8, 
        label="学校コード", 
        help_text="学校から配布された8桁のコードを入力してください"
    )

    class Meta(UserCreationForm.Meta):
        model = User

    # ★ 追加: 入力されたコードが正しいかチェックする
    def clean_school_code(self):
        code = self.cleaned_data.get('school_code')
        if not School.objects.filter(code=code).exists():
            raise ValidationError("無効な学校コードです。正しいコードを入力してください。")
        return code

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            
            # ★ コードから学校を特定して紐付ける
            code = self.cleaned_data.get('school_code')
            school = School.objects.get(code=code)
            
            Student.objects.create(
                user=user,
                full_name=self.cleaned_data.get('full_name'),
                grade=self.cleaned_data.get('grade'),
                school=school  # ★ ここで学校を保存
            )
        return user

# ---------------------------------------------------------
# 2. 教員用サインアップフォーム (★修正: 学校コード対応)
# ---------------------------------------------------------
class TeacherSignUpForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, label="氏名")
    subject = forms.CharField(max_length=50, label="担当教科")
    
    # ★ 変更: 所属学校選択を削除し、コード入力に変更
    school_code = forms.CharField(
        max_length=8, 
        label="学校コード",
        help_text="所属学校の8桁のコードを入力してください"
    )

    class Meta(UserCreationForm.Meta):
        model = User
    
    # ★ 追加: コードのチェック
    def clean_school_code(self):
        code = self.cleaned_data.get('school_code')
        if not School.objects.filter(code=code).exists():
            raise ValidationError("無効な学校コードです。正しいコードを入力してください。")
        return code

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()
        
        # ★ コードから学校を特定
        code = self.cleaned_data.get('school_code')
        school = School.objects.get(code=code)
        
        Teacher.objects.create(
            user=user,
            full_name=self.cleaned_data.get('full_name'),
            subject=self.cleaned_data.get('subject'),
            school=school  # ★ ここで学校を保存
        )
        return user

# 3. 企業担当者用サインアップフォーム
class CompanyRepresentativeSignUpForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, label="担当者名")
    department = forms.CharField(max_length=100, label="所属部署", required=False)
    
    # ★ 追加: 求人票URL入力欄
    job_offer_url = forms.URLField(
        label="求人票URL", 
        required=False,
        widget=forms.URLInput(attrs={'placeholder': 'https://...'})
    )

    job_offer_pdf = forms.FileField(
        label="求人票PDF",
        required=False,
        help_text="求人票のPDFファイルがあればアップロードしてください"
    )

    company_code = forms.CharField(
        max_length=8,
        label="企業コード",
        help_text="所属企業の8桁のコードを入力してください"
    )

    class Meta(UserCreationForm.Meta):
        model = User
    
    def clean_company_code(self):
        code = self.cleaned_data.get('company_code')
        if not Company.objects.filter(code=code).exists():
            raise ValidationError("無効な企業コードです。正しいコードを入力してください。")
        return code

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()
        
        code = self.cleaned_data.get('company_code')
        company = Company.objects.get(code=code)
        
        CompanyRepresentative.objects.create(
            user=user,
            full_name=self.cleaned_data.get('full_name'),
            department=self.cleaned_data.get('department'),
            company=company,
            job_offer_url=self.cleaned_data.get('job_offer_url'),
            job_offer_pdf=self.cleaned_data.get('job_offer_pdf')
        )
        return user
# ---------------------------------------------------------
# その他のフォーム (変更なし)
# ---------------------------------------------------------
class TeacherCommentForm(forms.ModelForm):
    comment = forms.CharField(
        label="学生への推薦コメント・指導状況",
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'rows': 5})
    )
    class Meta:
        model = Student
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 5}),
        }

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['full_name', 'grade', 'school', 'is_public_to_companies']
        labels = {
            'full_name': '氏名',
            'grade': '学年',
            'school': '所属学校',
            'is_public_to_companies': '企業へのプロフィール公開',
        }

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
    # ★ 企業のHPもここで編集できるようにフィールドを追加する場合
    website_url = forms.URLField(label="企業ホームページ", required=False)

    class Meta:
        model = CompanyRepresentative
        fields = ['full_name', 'department', 'job_offer_url', 'job_offer_pdf'] # ★ job_offer_urlを追加
        labels = {
            'full_name': '担当者氏名',
            'department': '所属部署',
            'job_offer_url': '求人票URL',
            'job_offer_pdf': '求人票PDF',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # フォーム初期化時に、Companyモデルにある現在のHPのURLを表示する
        if self.instance and self.instance.company:
            self.fields['website_url'].initial = self.instance.company.website_url

    def save(self, commit=True):
        # 担当者情報の保存
        representative = super().save(commit=False)
        if commit:
            representative.save()
            
            # 企業HP情報の保存（Companyモデル側の更新）
            company = representative.company
            company.website_url = self.cleaned_data['website_url']
            company.save()
        return representative