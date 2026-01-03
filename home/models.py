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
    custom_avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='カスタムアバター画像')
    background_color = models.CharField(max_length=7, default='#fffff0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_avatar_url(self):
        """アバター画像のURLを取得"""
        if self.custom_avatar:
            return self.custom_avatar.url
        return f'/static/home/images/django icon/{self.avatar_image}'


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
    
    # AI生成用または個別設定用
    avatar_image = models.CharField(max_length=100, blank=True, null=True)
    background_color = models.CharField(max_length=7, blank=True, null=True)
    is_ai_generated = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False, verbose_name='公開する')
    
    # 管理者専用機能
    is_pinned = models.BooleanField(default=False, verbose_name='ピン留め（おすすめ）')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def card_count(self):
        return self.cards.count()

    def get_avatar_url(self):
        """単語帳固有のアバター画像があればそれを返し、なければ作成者のプロファイル画像を返す"""
        if self.avatar_image:
            return f'/static/home/images/django icon/{self.avatar_image}'
        return self.user.profile.get_avatar_url()

    def get_background_color(self):
        """単語帳固有の背景色があればそれを返し、なければ作成者のプロファイル背景色を返す"""
        if self.background_color:
            return self.background_color
        return self.user.profile.background_color

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


# 単語カードのスター（お気に入り）機能
class WordCardStar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='starred_cards')
    wordcard = models.ForeignKey(WordCard, on_delete=models.CASCADE, related_name='stars')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'wordcard')
        indexes = [models.Index(fields=['user', 'wordcard'])]

    def __str__(self):
        return f"{self.user.username} starred {self.wordcard.front_text}"
