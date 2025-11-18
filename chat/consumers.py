# chat/consumers.py

import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from .models import ChatRoom, ChatMessage
from accounts.models import Student, Teacher, CompanyRepresentative
from django.utils import timezone # ★ 1. timezone をインポート

class ChatConsumer(WebsocketConsumer):
    
 
    def get_display_name(self, user):
        """ ユーザーオブジェクトから、チャット用の表示名を取得する """
        try:
            if hasattr(user, 'student'):
                profile = user.student
                school_name = profile.school.name if profile.school else "所属未設定"
                return f"{profile.full_name}（{school_name}）"
                
            elif hasattr(user, 'teacher'):
                profile = user.teacher
                school_name = profile.school.name if profile.school else "所属未設定"
                return f"{profile.full_name} 先生（{school_name}）"
                
            elif hasattr(user, 'companyrepresentative'):
                profile = user.companyrepresentative
                company_name = profile.company.name if profile.company else "所属未設定"
                return f"{profile.full_name} 様（{company_name}）"
                
            elif user.is_superuser:
                return f"{user.username} (管理者)"
                
        except Exception:
            # (もし school や company が None でエラーになっても)
            pass 
            
        # 例外が発生した場合や、どのプロフィールにも当てはまらない場合は
        # ユーザーIDをそのまま返す
        return user.username


    def connect(self):
        # (connect メソッドは変更なし)
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        user = self.scope['user']
        
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            if user not in room.participants.all():
                self.close()
                return
        except ChatRoom.DoesNotExist:
            self.close()
            return
            
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # (disconnect メソッドは変更なし)
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        
        user = self.scope['user']
        display_name = self.get_display_name(user)
        
        print(f"Room {self.room_id} | User {display_name} | Message: {message_content}")

        try:
            room = ChatRoom.objects.get(id=self.room_id)
            new_message = ChatMessage.objects.create(
                room=room,
                author=user,
                content=message_content
            )
        except:
            self.send(text_data=json.dumps({'error': 'Message could not be saved.'}))
            return
        
        # ★ 2. タイムスタンプをローカルタイム（日本時間）に変換
        local_timestamp = timezone.localtime(new_message.timestamp)
        # グループ（同じ部屋にいる全員）にメッセージをブロードキャスト
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message', 
                'message': new_message.content,
                'author_username': display_name,
                
                # ↓↓ この行を追記 ↓↓
                'author_id': user.id, # ★ JSが「自分」か「相手」か判定するためにIDを送る
                
                'timestamp': local_timestamp.strftime('%H:%M')
            }
        )

    # ブロードキャストされたメッセージを個々のWebSocketに送信する処理
    def chat_message(self, event):
        message = event['message']
        author_username = event['author_username']
        timestamp = event['timestamp']
        
        # ↓↓ この行を追記 ↓↓
        author_id = event['author_id'] # ★ author_id もJSに渡す

        self.send(text_data=json.dumps({
            'message': message,
            'author_username': author_username,
            'author_id': author_id, # ★ 追記
            'timestamp': timestamp,
        }))