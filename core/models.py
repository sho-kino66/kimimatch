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