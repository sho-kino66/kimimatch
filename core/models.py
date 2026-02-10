from django.db import models
from django.utils import timezone

class Announcement(models.Model):
    title = models.CharField(max_length=200, verbose_name="タイトル")
    content = models.TextField(verbose_name="本文")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="作成日時")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "お知らせ"
        verbose_name_plural = "お知らせ一覧"

class Tag(models.Model):
    # ★ カテゴリの選択肢を定義
    CATEGORY_CHOICES = (
        ('strength', '強み・スキル'),   # 人柄やスキルなど
        ('condition', '条件・待遇'),     # 給与や休日など
        ('both', 'その他・両方'),       # どちらにも出したい場合
    )

    name = models.CharField(max_length=50, unique=True, verbose_name="タグ名")
    
    # ★ カテゴリフィールドを追加
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='both', # 既存のタグは一旦「両方」になります
        verbose_name="カテゴリー"
    )
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "タグ"
        verbose_name_plural = "タグ一覧"

class Inquiry(models.Model):
    name = models.CharField(max_length=100, verbose_name="お名前")
    email = models.EmailField(verbose_name="メールアドレス")
    subject = models.CharField(max_length=200, verbose_name="件名")
    message = models.TextField(verbose_name="お問い合わせ内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="送信日")

    class Meta:
        verbose_name = "お問い合わせ"         
        verbose_name_plural = "お問い合わせ"

    def __str__(self):
        return f"{self.name} - {self.subject}"

class SchoolApplication(models.Model):
    school_name = models.CharField(max_length=100, verbose_name="学校名")
    contact_name = models.CharField(max_length=100, verbose_name="担当者名")
    email = models.EmailField(verbose_name="メールアドレス")
    phone = models.CharField(max_length=20, verbose_name="電話番号")
    address = models.CharField(max_length=255, verbose_name="住所")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="申込日")

    class Meta:
        verbose_name = "学校申し込み"
        verbose_name_plural = "学校申し込み一覧"

    def __str__(self):
        return self.school_name

class CompanyApplication(models.Model):
    company_name = models.CharField(max_length=100, verbose_name="企業名")
    contact_name = models.CharField(max_length=100, verbose_name="担当者名")
    email = models.EmailField(verbose_name="メールアドレス")
    phone = models.CharField(max_length=20, verbose_name="電話番号")
    address = models.CharField(max_length=255, verbose_name="住所")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="申込日")

    class Meta:
        verbose_name = "企業申し込み"
        verbose_name_plural = "企業申し込み一覧"

    def __str__(self):
        return self.company_name