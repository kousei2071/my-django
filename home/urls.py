from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('wordbooks/', views.wordbook_list, name='wordbook_list'),
    path('wordbooks/create/', views.wordbook_create, name='wordbook_create'),
    path('wordbooks/<int:pk>/', views.wordbook_detail, name='wordbook_detail'),
    path('wordbooks/<int:wordbook_pk>/cards/create/', views.wordcard_create, name='wordcard_create'),
    path('wordcards/<int:pk>/delete/', views.wordcard_delete, name='wordcard_delete'),
]
