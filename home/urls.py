from django.urls import path
from . import views

urlpatterns = [
    path('', views.wordbook_list, name='home'),
    path('mypage/', views.mypage, name='mypage'),
    path('mypage/wordbooks/', views.my_wordbooks_all, name='mypage_wordbooks_all'),
    path('mypage/bookmarks/', views.bookmarked_wordbooks_all, name='mypage_bookmarks_all'),
    # Avatar APIs
    path('api/avatars/', views.get_available_avatars, name='get_avatars'),
    path('api/avatar/update/', views.update_avatar, name='update_avatar'),
    path('api/backgrounds/', views.get_available_backgrounds, name='get_backgrounds'),
    path('api/background/update/', views.update_background, name='update_background'),
    # Tag APIs
    path('tags/', views.tags_list, name='tags_list'),
    path('tags/create/', views.tag_create, name='tag_create'),
    path('tags/<int:pk>/delete/', views.tag_delete, name='tag_delete'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('wordbooks/', views.wordbook_list, name='wordbook_list'),
    path('wordbooks/create/', views.wordbook_create, name='wordbook_create'),
    path('wordbooks/<int:pk>/', views.wordbook_detail, name='wordbook_detail'),
    path('wordbooks/<int:pk>/tags/', views.wordbook_update_tags, name='wordbook_update_tags'),
    path('wordbooks/<int:pk>/bookmark/', views.wordbook_bookmark_toggle, name='wordbook_bookmark'),
    path('wordbooks/<int:wordbook_pk>/cards/create/', views.wordcard_create, name='wordcard_create'),
    path('wordcards/<int:pk>/delete/', views.wordcard_delete, name='wordcard_delete'),
    path('wordbooks/<int:pk>/like/', views.wordbook_like_toggle, name='wordbook_like'),
]
