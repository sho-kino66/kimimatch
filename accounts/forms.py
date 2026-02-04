from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction

from companies.models import Company, CompanyTag
from schools.models import School
from core.models import Tag
from .models import Student, Teacher, CompanyRepresentative, StudentTag

# =========================================================
# 1. サインアップ用フォーム（コード認証機能付き）
# =========================================================

class StudentSignUpForm(UserCreationForm):
    """学生用：学校コードを入力して登録"""
    full_name = forms.CharField(max_length=100, label="氏名")
    grade = forms.ChoiceField(
        choices=Student.GRADE_CHOICES, 
        label="学年",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    school_code = forms.CharField(
        max_length=8, 
        label="学校コード", 
        help_text="学校から配布された8桁のコードを入力してください"
    )

    class Meta(UserCreationForm.Meta):
        model = User

    def clean_school_code(self):
        code = self.cleaned_data.get('school_code')
        if not School.objects.filter(code=code).exists():
            raise ValidationError("無効な学校コードです。正しいコードを入力してください。")
        return code

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()
        code = self.cleaned_data.get('school_code')
        school = School.objects.get(code=code)
        
        Student.objects.create(
            user=user,
            full_name=self.cleaned_data.get('full_name'),
            grade=self.cleaned_data.get('grade'),
            school=school
        )
        return user

class TeacherSignUpForm(UserCreationForm):
    """教員用：学校コードを入力して登録"""
    full_name = forms.CharField(max_length=100, label="氏名")
    subject = forms.CharField(max_length=50, label="担当教科")
    school_code = forms.CharField(
        max_length=8, 
        label="学校コード",
        help_text="所属学校の8桁のコードを入力してください"
    )

    class Meta(UserCreationForm.Meta):
        model = User
    
    def clean_school_code(self):
        code = self.cleaned_data.get('school_code')
        if not School.objects.filter(code=code).exists():
            raise ValidationError("無効な学校コードです。正しいコードを入力してください。")
        return code

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()
        code = self.cleaned_data.get('school_code')
        school = School.objects.get(code=code)
        
        Teacher.objects.create(
            user=user,
            full_name=self.cleaned_data.get('full_name'),
            subject=self.cleaned_data.get('subject'),
            school=school
        )
        return user

class CompanyRepresentativeSignUpForm(UserCreationForm):
    """企業担当者用：企業コードを入力して登録"""
    full_name = forms.CharField(max_length=100, label="担当者名")
    department = forms.CharField(max_length=100, label="所属部署", required=False)
    job_offer_url = forms.URLField(
        label="求人票URL", required=False,
        widget=forms.URLInput(attrs={'placeholder': 'https://...'})
    )
    job_offer_pdf = forms.FileField(label="求人票PDF", required=False)
    company_code = forms.CharField(
        max_length=8, label="企業コード",
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

# =========================================================
# 2. プロフィール編集用フォーム（所属ロック機能付き）
# =========================================================

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['full_name', 'grade', 'school', 'is_public_to_companies']
        labels = {
            'full_name': '氏名', 'grade': '学年', 'school': '所属学校',
            'is_public_to_companies': '企業へのプロフィール公開',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ★ 所属学校を編集不可にする
        if 'school' in self.fields:
            self.fields['school'].disabled = True

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['full_name', 'subject', 'school']
        labels = {'full_name': '氏名', 'subject': '担当教科', 'school': '所属学校'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ★ 所属学校を編集不可にする
        if 'school' in self.fields:
            self.fields['school'].disabled = True

class CompanyRepresentativeProfileForm(forms.ModelForm):
    website_url = forms.URLField(label="企業ホームページ", required=False)

    class Meta:
        model = CompanyRepresentative
        fields = ['full_name', 'department', 'company', 'job_offer_url', 'job_offer_pdf']
        labels = {
            'full_name': '担当者氏名', 'department': '所属部署', 'company': '所属企業',
            'job_offer_url': '求人票URL', 'job_offer_pdf': '求人票PDF',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.company:
            self.fields['website_url'].initial = self.instance.company.website_url
        # ★ 所属企業を編集不可にする
        if 'company' in self.fields:
            self.fields['company'].disabled = True

    def save(self, commit=True):
        representative = super().save(commit=False)
        if commit:
            representative.save()
            company = representative.company
            company.website_url = self.cleaned_data['website_url']
            company.save()
        return representative

# =========================================================
# 3. タグ設定・推薦フォーム
# =========================================================

class StudentTagUpdateForm(forms.Form):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.strength_tags = Tag.objects.filter(category__in=['strength', 'both'])
        self.condition_tags = Tag.objects.filter(category__in=['condition', 'both'])
        for i in range(1, 6):
            self.fields[f'strength_{i}'] = forms.ModelChoiceField(
                queryset=self.strength_tags, label=f'自分の強み {i}位', required=False,
                widget=forms.Select(attrs={'class': 'form-control'})
            )
            self.fields[f'desire_{i}'] = forms.ModelChoiceField(
                queryset=self.condition_tags, label=f'会社に求めるもの {i}位', required=False,
                widget=forms.Select(attrs={'class': 'form-control'})
            )

    def save(self):
        student = self.user.student
        StudentTag.objects.filter(student=student).delete()
        for key, value in self.cleaned_data.items():
            if value:
                tag_type, rank_str = key.split('_')
                StudentTag.objects.create(student=student, tag=value, tag_type=tag_type, rank=int(rank_str))

class CompanyTagUpdateForm(forms.Form):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.strength_tags = Tag.objects.filter(category__in=['strength', 'both'])
        self.condition_tags = Tag.objects.filter(category__in=['condition', 'both'])
        for i in range(1, 6):
            self.fields[f'strength_{i}'] = forms.ModelChoiceField(
                queryset=self.strength_tags, label=f'求める人材の強み {i}位', required=False,
                widget=forms.Select(attrs={'class': 'form-control'})
            )
            self.fields[f'feature_{i}'] = forms.ModelChoiceField(
                queryset=self.condition_tags, label=f'自社の特徴・政策 {i}位', required=False,
                widget=forms.Select(attrs={'class': 'form-control'})
            )

    def save(self):
        company = self.user.companyrepresentative.company
        CompanyTag.objects.filter(company=company).delete()
        for key, value in self.cleaned_data.items():
            if value:
                tag_type, rank_str = key.split('_')
                CompanyTag.objects.create(company=company, tag=value, tag_type=tag_type, rank=int(rank_str))

class TeacherCommentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['comment']
        widgets = {'comment': forms.Textarea(attrs={'rows': 5, 'placeholder': '学生の推薦コメントを入力してください'})}