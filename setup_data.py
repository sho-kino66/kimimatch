from core.models import Announcement, Tag
from django.utils import timezone

# --- 1. タグデータの作成 ---
tags_data = [
    # 強み・スキル
    {'name': '粘り強さ', 'category': 'strength'},
    {'name': '協調性', 'category': 'strength'},
    {'name': '傾聴力', 'category': 'strength'},
    {'name': '行動力・フットワーク', 'category': 'strength'},
    {'name': '有資格者', 'category': 'strength'},
    {'name': 'リーダーシップ', 'category': 'strength'},
    {'name': '論理的思考力', 'category': 'strength'},
    
    # 条件・待遇
    {'name': '年間休日120日以上', 'category': 'condition'},
    {'name': '福利厚生充実', 'category': 'condition'},
    {'name': 'フレックスタイム制', 'category': 'condition'},
    {'name': 'リモートワーク可', 'category': 'condition'},
    {'name': '月給20万円以上', 'category': 'condition'},
    {'name': '月給25万円以上', 'category': 'condition'},
    {'name': '月給30万円以上', 'category': 'condition'},
    
    # その他・両方
    {'name': '未経験歓迎', 'category': 'both'},
    {'name': '研修制度あり', 'category': 'both'},
]

print("--- タグの作成開始 ---")
for data in tags_data:
    tag, created = Tag.objects.get_or_create(
        name=data['name'],
        defaults={'category': data['category']}
    )
    if created:
        print(f"[作成] {tag.name}")
    else:
        if tag.category != data['category']:
            tag.category = data['category']
            tag.save()
            print(f"[更新] {tag.name}")
        else:
            print(f"[既存] {tag.name}")

# --- 2. お知らせデータの作成 ---
announcements_data = [
    {
        'title': 'KimiMatchへようこそ！',
        'content': '学生と企業をつなぐ新しいプラットフォーム「KimiMatch」がオープンしました。\nまずはプロフィール設定から「マッチング用タグ」を設定してみましょう！'
    },
    {
        'title': 'システムメンテナンスのお知らせ',
        'content': 'サービスの安定稼働のため、以下の日程でサーバーメンテナンスを実施します。\n\n日時：2025年12月10日 AM 2:00 - AM 5:00\n\nご不便をおかけしますが、よろしくお願いいたします。'
    },
    {
        'title': '【新機能】マッチ度計算機能を追加しました',
        'content': '企業詳細ページにて、あなたとの相性（マッチ度）がパーセント表示されるようになりました。\nお互いの「強み」や「求める条件」がどれくらい一致しているか確認してみましょう。'
    },
]

print("\n--- お知らせの作成開始 ---")
for data in announcements_data:
    obj, created = Announcement.objects.get_or_create(
        title=data['title'],
        defaults={
            'content': data['content'],
            'created_at': timezone.now()
        }
    )
    if created:
        print(f"[作成] {obj.title}")
    else:
        print(f"[既存] {obj.title}")

print("\n完了しました。")