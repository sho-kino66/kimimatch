from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Announcement

# トップページを表示するための「関数（機能）」
def top_page(request):
    # 2. もしユーザーがログイン済みなら
    if request.user.is_authenticated:
        # 3. トップページではなく、ダッシュボードにリダイレクトする
        return redirect('accounts:dashboard')
    
    context = {
        'message': 'トップページへようこそ！',
    }

    # 'core/top_page.html' というテンプレートを context のデータで表示する
    return render(request, 'core/top_page.html', context)

# お知らせ詳細ビュー (今回追加する機能)
@login_required
def announcement_detail(request, pk):
    # URLから渡されたpk(ID)を元に、お知らせを1つ取得する
    announcement = get_object_or_404(Announcement, pk=pk)
    
    context = {
        'announcement': announcement,
    }
    return render(request, 'core/announcement_detail.html', context)