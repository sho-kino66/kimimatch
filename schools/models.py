from django.db import models
import secrets
import string

# ランダムな8文字のコードを生成する関数
def generate_school_code():
    # 英大文字(A-Z)と数字(0-9)からランダムに選ぶ
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(8))

class School(models.Model):
    name = models.CharField(max_length=100, verbose_name="学校名")
    address = models.CharField(max_length=255, verbose_name="住所")
    
    # 追加: 学校コード (自動生成、重複不可)
    code = models.CharField(
        max_length=8, 
        default=generate_school_code, 
        unique=True, 
        editable=False,  # 管理画面で勝手に書き換えられないようにする
        verbose_name="学校コード"
    )
    
    def __str__(self):
        return f"{self.name} ({self.code})"
        
    class Meta:
        verbose_name = "学校"
        verbose_name_plural = "学校一覧"