from .models import Student, Teacher, CompanyRepresentative

def add_user_role(request):
    """
    すべてのテンプレートに 'user_type' という変数を自動で追加する
    """
    user = request.user
    
    # ログインしていない場合は 'guest'
    if not user.is_authenticated:
        return {'user_type': 'guest'}
    
    # ログイン中のユーザーの種類を判別
    try:
        if hasattr(user, 'student'):
            return {'user_type': 'student'}
        elif hasattr(user, 'teacher'):
            return {'user_type': 'teacher'}
        elif hasattr(user, 'companyrepresentative'):
            return {'user_type': 'company'}
        elif user.is_superuser:
            return {'user_type': 'admin'}
        else:
            return {'user_type': 'authenticated'} # (プロフィール未設定)
            
    except Exception:
        # (エラーが発生した場合)
        return {'user_type': 'guest'}