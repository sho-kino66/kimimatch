# chat/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import ChatRoom, ChatMessage
from django.db.models import Q, Count, OuterRef, Subquery
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseForbidden

# ★ 1. モデルをインポート
from accounts.models import Student, Teacher, CompanyRepresentative

# ★ 2. === ヘルパー関数 (consumers.py からコピー) ===
def get_display_name(user):
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
        pass 
        
    return user.username
# === ヘルパー関数ここまで ===


@login_required
def chat_test_room(request):
    return render(request, 'chat/chat_test_room.html')

@login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    room = ChatRoom.objects.annotate(
        num_participants=Count('participants')
    ).filter(
        num_participants=2,
        participants=request.user
    ).filter(
        participants=other_user
    ).first()

    if not room:
        room = ChatRoom.objects.create()
        room.participants.add(request.user, other_user)
        
    next_url = request.GET.get('next', reverse_lazy('chat:chat_list'))
    
    redirect_url = f"{reverse('chat:chat_room', args=[room.id])}?next={next_url}"
    
    return redirect(redirect_url)


# ★ 3. === chat_room ビューを修正 ===
@login_required
def chat_room(request, room_id):
    try:
        room = ChatRoom.objects.get(id=room_id)
        
        if request.user not in room.participants.all():
            return redirect('accounts:dashboard')
            
        # 過去のメッセージを取得 (author情報も一緒に取得)
        messages = room.messages.all().select_related('author').order_by('timestamp')
        
        # ★ 過去のメッセージにも表示名を追加
        for msg in messages:
            msg.author_display_name = get_display_name(msg.author)
            
    except ChatRoom.DoesNotExist:
        return redirect('accounts:dashboard')

    default_back_url = reverse_lazy('chat:chat_list')
    back_url = request.GET.get('next', default_back_url)
    
    if not back_url or not back_url.startswith('/'):
        back_url = default_back_url

    context = {
        'room': room,
        'room_id': room.id,
        'messages': messages, # ★ 表示名が追加されたメッセージリスト
        'back_url': back_url,
    }
    
    return render(request, 'chat/chat_room.html', context)


# チャット一覧（受信箱）
class ChatRoomListView(LoginRequiredMixin, ListView):
    model = ChatRoom
    template_name = 'chat/chat_list.html'
    context_object_name = 'chat_rooms'
    
    def get_queryset(self):
        user = self.request.user
        
        last_message = ChatMessage.objects.filter(
            room=OuterRef('pk')
        ).order_by('-timestamp')

        queryset = ChatRoom.objects.filter(
            participants=user
        ).annotate(
            last_message_timestamp=Subquery(last_message.values('timestamp')[:1]),
            last_message_content=Subquery(last_message.values('content')[:1]),
            other_participant_id=Subquery(
                ChatRoom.participants.through.objects.filter(
                    chatroom=OuterRef('pk')
                ).exclude(
                    user=user
                ).values('user_id')[:1]
            )
        ).order_by('-last_message_timestamp')
        
        other_user_ids = [room.other_participant_id for room in queryset if room.other_participant_id]
        other_users = User.objects.in_bulk(other_user_ids)

        # ★ ここも修正: 一覧画面の「相手」の表示名も取得
        for room in queryset:
            other_user = other_users.get(room.other_participant_id)
            if other_user:
                room.other_participant_display_name = get_display_name(other_user)
            else:
                room.other_participant_display_name = "（不明な相手）"
            
        return queryset