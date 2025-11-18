from django.db import models
from .validators import validate_file_extension
# ↓↓ 循環インポートエラーを避けるため、直接インポートしない
# from accounts.models import Student 

class Portfolio(models.Model):
    # ↓↓ 文字列で 'accounts.Student' を指定する
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, verbose_name="学生")
    
    title = models.CharField(max_length=200, verbose_name="タイトル")
    description = models.TextField(verbose_name="説明文")
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


class PortfolioItem(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="items")
    
    # ★ validators を追加し、help_text でユーザーに案内を表示
    file = models.FileField(
        upload_to='portfolio_files/', 
        verbose_name="成果物ファイル",
        validators=[validate_file_extension],
        help_text="PDF, 画像(JPG/PNG), またはソースコード一式(ZIP)をアップロードしてください。"
    )
    
    def __str__(self):
        return f"{self.portfolio.title} の添付ファイル"
    
    def delete(self, *args, **kwargs):
        self.file.delete(save=False)
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "ポートフォリオ作品"
        verbose_name_plural = "ポートフォリオ作品"