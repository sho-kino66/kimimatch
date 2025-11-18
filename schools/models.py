from django.db import models

class School(models.Model):
    name = models.CharField(max_length=100, verbose_name="学校名")
    address = models.CharField(max_length=255, verbose_name="住所")
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = "学校"
        verbose_name_plural = "学校一覧"