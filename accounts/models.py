from django.db import models
from django.contrib.auth.models import User
# from schools.models import School # (循環インポート回避のため文字列指定)

# 学生プロフィール
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey('schools.School', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所属学校")
    full_name = models.CharField(max_length=100, verbose_name="氏名")
    grade = models.IntegerField(verbose_name="学年")
    
    comment = models.TextField(
        verbose_name="教員からのコメント", 
        blank=True,
        null=True
    )
    comment_teacher = models.ForeignKey(
        'Teacher', 
        on_delete=models.SET_NULL,
        verbose_name="コメント記入教員",
        blank=True,
        null=True
    )
    
    is_public_to_companies = models.BooleanField(
        verbose_name="企業へのプロフィール公開",
        default=True 
    )

    def __str__(self):
        return self.full_name
    
    class Meta:
        verbose_name = "学生プロフィール"
        verbose_name_plural = "学生プロフィール"

# 教員プロフィール
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey('schools.School', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所属学校")
    full_name = models.CharField(max_length=100, verbose_name="氏名")
    subject = models.CharField(max_length=50, verbose_name="担当教科")
    
    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "教員プロフィール"
        verbose_name_plural = "教員プロフィール"

# 企業担当者プロフィール
class CompanyRepresentative(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, verbose_name="所属企業")
    full_name = models.CharField(max_length=100, verbose_name="担当者名")
    department = models.CharField(max_length=100, verbose_name="所属部署", blank=True)

    def __str__(self):
        return f"{self.company.name} - {self.full_name}"

    class Meta:
        verbose_name = "企業担当者"
        verbose_name_plural = "企業担当者"

# 学生のお気に入り企業
class FavoriteCompany(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'company')
        verbose_name = "お気に入り企業"
        verbose_name_plural = "お気に入り企業一覧"

    def __str__(self):
        return f"{self.student.full_name}のお気に入り ({self.company.name})"