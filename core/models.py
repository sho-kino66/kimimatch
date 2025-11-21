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