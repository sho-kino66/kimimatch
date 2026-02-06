from django.db import models
from django.core.validators import MaxLengthValidator  # ★追加
from .validators import validate_file_extension

class Portfolio(models.Model):
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, verbose_name="学生")
    
    # タイトル：200文字から30文字に制限
    title = models.CharField(
        max_length=30, 
        verbose_name="タイトル"
    )
    
    # 説明文：MaxLengthValidatorを使用して300文字に制限
    description = models.TextField(
        verbose_name="説明文",
        validators=[MaxLengthValidator(300)]  # ★追加
    )
    
    teacher_comment = models.TextField(
        verbose_name="教員からのコメント",
        blank=True,
        null=True
    )
    commenting_teacher = models.ForeignKey(
        'accounts.Teacher', 
        on_delete=models.SET_NULL,
        verbose_name="コメント記入教員",
        blank=True,
        null=True
    )
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "ポートフォリオ（表紙）"
        verbose_name_plural = "ポートフォリオ（表紙）"

# --- PortfolioItem は変更なし ---
class PortfolioItem(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="items")
    file = models.FileField(
        upload_to='portfolio_files/', 
        verbose_name="成果物ファイル",
        validators=[validate_file_extension],
        help_text="PDF, 画像(JPG/PNG), またはソースコード一式(ZIP)をアップロードしてください。"
    )

    ai_score = models.IntegerField(verbose_name="AI点数", blank=True, null=True)
    ai_feedback = models.TextField(verbose_name="AIフィードバック", blank=True, null=True)
    
    def __str__(self):
        return f"{self.portfolio.title} の添付ファイル"
    
    def delete(self, *args, **kwargs):
        self.file.delete(save=False)
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "ポートフォリオ作品"
        verbose_name_plural = "ポートフォリオ作品"