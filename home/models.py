from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ユーザープロファイル画像モデル
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_image = models.CharField(max_length=100, default='account.png', choices=[
        ('account.png', 'Account 1'),
        ('account2.png', 'Account 2'),
        ('account3.png', 'Account 3'),
        ('account4.png', 'Account 4'),
        ('account5.png', 'Account 5'),
        ('account6.png', 'Account 6'),
        ('account7.png', 'Account 7'),
        ('account8.png', 'Account 8'),
    ])
    background_color = models.CharField(max_length=7, default='#fffff0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tags')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

# 単語帳モデル
class WordBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wordbooks')
    title = models.CharField(max_length=200, verbose_name='単語帳名')
    description = models.TextField(blank=True, verbose_name='説明')
    tags = models.ManyToManyField('Tag', related_name='wordbooks', blank=True)
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
    
#いいね機能
class wordBookLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_wordbooks')
    wordbook = models.ForeignKey(WordBook, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'wordbook')
        indexes = [models.Index(fields=['user', 'wordbook'])]

    def __str__(self):
        return f"{self.user.username} ❤ {self.wordbook.title}"


# ブックマーク機能
class WordBookBookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarked_wordbooks')
    wordbook = models.ForeignKey(WordBook, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'wordbook')
        indexes = [models.Index(fields=['user', 'wordbook'])]

    def __str__(self):
        return f"{self.user.username} -> {self.wordbook.title}"
