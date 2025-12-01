from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),  # 単語帳一覧がホームページ
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('my-wordbooks/', views.my_wordbooks, name='my_wordbooks'),  # マイページ
    path('profile/edit/', views.profile_edit, name='profile_edit'),  # プロフィール編集
    path('wordbooks/create/', views.wordbook_create, name='wordbook_create'),
    path('wordbooks/<int:pk>/', views.wordbook_detail, name='wordbook_detail'),
    path('wordbooks/<int:wordbook_pk>/cards/create/', views.wordcard_create, name='wordcard_create'),
    path('wordcards/<int:pk>/delete/', views.wordcard_delete, name='wordcard_delete'),
    # クイズ機能（認証不要でアクセス可能）
    path('quiz/<int:pk>/start/', views.quiz_start, name='quiz_start'),
    path('quiz/question/', views.quiz_question, name='quiz_question'),
    path('quiz/answer/', views.quiz_answer, name='quiz_answer'),
    path('quiz/result/', views.quiz_result, name='quiz_result'),
]
