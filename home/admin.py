from django.contrib import admin
from .models import WordBook, WordCard

@admin.register(WordBook)
class WordBookAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'card_count', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(WordCard)
class WordCardAdmin(admin.ModelAdmin):
    list_display = ['front_text', 'back_text', 'wordbook', 'created_at']
    list_filter = ['wordbook', 'created_at']
    search_fields = ['front_text', 'back_text']
    readonly_fields = ['created_at', 'updated_at']
