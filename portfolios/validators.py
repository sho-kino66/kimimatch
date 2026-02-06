import os
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    # 1. 拡張子のチェック
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.zip', '.py', '.html', '.css', '.js']
    
    if not ext.lower() in valid_extensions:
        raise ValidationError(
            f'未対応のファイル形式です。以下の形式がアップロード可能です: {", ".join(valid_extensions)}'
        )

    # 2. ファイルサイズのチェック（5MB制限）
    limit = 5 * 1024 * 1024  # 5MBをバイト換算
    if value.size > limit:
        raise ValidationError('ファイルサイズが大きすぎます。5MB以下のファイルをアップロードしてください。')