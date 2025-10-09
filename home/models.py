from django.db import models
from django.contrib.auth.models import User

# 単語帳モデル
class WordBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wordbooks')
    title = models.CharField(max_length=200, verbose_name='単語帳名')
    description = models.TextField(blank=True, verbose_name='説明')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def card_count(self):
        return self.cards.count()

# 単語カードモデル
class WordCard(models.Model):
    wordbook = models.ForeignKey(WordBook, on_delete=models.CASCADE, related_name='cards')
    front_text = models.CharField(max_length=200, verbose_name='表面(英単語)')
    back_text = models.TextField(verbose_name='裏面(意味)')
    image = models.ImageField(upload_to='word_images/', blank=True, null=True, verbose_name='画像')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.front_text} - {self.back_text}"
