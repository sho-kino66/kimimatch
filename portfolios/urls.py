from django.urls import path
from . import views 

app_name = 'portfolios' # ★ app_name を設定

urlpatterns = [
    # ポートフォリオ新規作成 (例: /portfolios/create/ )
    path('create/', views.PortfolioCreateView.as_view(), name='create'),

    # 詳細ページ (例: /portfolios/5/ )
    path('<int:pk>/', views.PortfolioDetailView.as_view(), name='detail'),
    
    # 編集ページ (例: /portfolios/5/update/ )
    path('<int:pk>/update/', views.PortfolioUpdateView.as_view(), name='update'),
    
    # 削除ページ (例: /portfolios/5/delete/ )
    path('<int:pk>/delete/', views.PortfolioDeleteView.as_view(), name='delete'),

    # 作品ファイル追加処理 (例: /portfolios/5/add_item/ )
    path('<int:portfolio_pk>/add_item/', views.add_portfolio_item, name='add_item'),

    # 作品ファイル削除 (例: /portfolios/item/12/delete/ )
    path('item/<int:pk>/delete/', views.PortfolioItemDeleteView.as_view(), name='delete_item'),

    # <int:pk> は「コメントを編集したいポートフォリオ(Portfolio)のID」
    path('portfolio/<int:pk>/comment/', views.PortfolioCommentUpdateView.as_view(), name='portfolio_comment_update'),
]