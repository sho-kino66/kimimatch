from django.db import models
from django.contrib.auth.models import User
from core.models import Tag
import secrets
import string

# ランダムな8文字のコードを生成する関数
def generate_company_code():
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(8))

class Company(models.Model):
    name = models.CharField(max_length=100, verbose_name="企業名")
    industry = models.CharField(max_length=100, verbose_name="業種")
    description = models.TextField(verbose_name="事業内容")
    
    # ★ 追加: 企業ホームページURL
    website_url = models.URLField(verbose_name="企業ホームページ", blank=True, null=True)

    # 企業コード
    code = models.CharField(
        max_length=8, 
        default=generate_company_code, 
        unique=True, 
        editable=False,
        verbose_name="企業コード"
    )
    
    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "企業"
        verbose_name_plural = "企業一覧"

# --- 以下変更なし (Scout, CompanyTag) ---
class Scout(models.Model):
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('company', 'student')
        verbose_name = "スカウト"
        verbose_name_plural = "スカウト一覧"

    def __str__(self):
        return f"{self.company.name}が{self.student.full_name}をスカウト"
    
class CompanyTag(models.Model):
    TAG_TYPE_CHOICES = (
        ('strength', '求める人材の強み'),
        ('feature', '自社の特徴・政策'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    tag_type = models.CharField(max_length=10, choices=TAG_TYPE_CHOICES)
    rank = models.IntegerField(verbose_name="順位", choices=[(i, f"{i}位") for i in range(1, 6)])

    class Meta:
        unique_together = ('company', 'tag_type', 'rank')
        ordering = ['tag_type', 'rank']