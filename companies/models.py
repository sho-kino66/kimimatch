from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    name = models.CharField(max_length=100, verbose_name="企業名")
    industry = models.CharField(max_length=100, verbose_name="業種")
    description = models.TextField(verbose_name="事業内容")
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "企業"
        verbose_name_plural = "企業一覧"

# 企業による学生スカウト
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