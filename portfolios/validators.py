import os
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # 拡張子を取得
    # 許可する拡張子リスト
    valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.zip', '.py', '.html', '.css', '.js']
    
    if not ext.lower() in valid_extensions:
        raise ValidationError(f'未対応のファイル形式です。以下の形式がアップロード可能です: {", ".join(valid_extensions)}')