from django.contrib import admin
from .models import WordBook, WordCard, Tag, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'avatar_image', 'background_color', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']

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

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'slug']
    readonly_fields = ['created_at', 'updated_at']
