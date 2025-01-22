from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import WordBook, WordCard
from django.db.models import Count
from django.urls import reverse
from .models import wordBookLike
# マイページ
@login_required
def mypage(request):
    # 自分の単語帳
    my_wordbooks = WordBook.objects.filter(user=request.user)
    nickname = request.user.first_name or request.user.username
    likes_total = 0  # TODO: 単語帳のいいね合計（実装予定）
    saved_wordbooks_count = 0  # TODO: 保存している単語帳数（実装予定）
    
    context = {
        'my_wordbooks': my_wordbooks,
        'nickname': nickname,
        'likes_total': likes_total,
        'saved_wordbooks_count': saved_wordbooks_count,
    }
    return render(request, 'home/mypage.html', context)

# ユーザー登録
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '会員登録が完了しました!')
            return redirect('mypage')
    else:
        form = UserCreationForm()
    return render(request, 'home/register.html', {'form': form})

# ログイン
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('mypage')
    else:
        form = AuthenticationForm()
    return render(request, 'home/login.html', {'form': form})

# ログアウト
def logout_view(request):
    logout(request)
    messages.success(request, 'ログアウトしました')
    return redirect('home')

# ホームページ（単語帳一覧）
def wordbook_list(request):
    # 人気の単語帳（全ユーザーの単語帳から取得）
    popular_wordbooks = WordBook.objects.all()[:6]
    
    # 既存の単語帳（全ユーザーの単語帳）
    existing_wordbooks = WordBook.objects.all()[:6]
    
    context = {
        'popular_wordbooks': WordBook.objects.annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')[:6],
        'existing_wordbooks': WordBook.objects.annotate(like_count=Count('likes')).order_by('-created_at')[:6]
    }
    return render(request, 'home/wordbook_list.html', context)

# 単語帳作成
@login_required
def wordbook_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        
        wordbook = WordBook.objects.create(
            user=request.user,
            title=title,
            description=description
        )
        messages.success(request, '単語帳を作成しました!')
        return redirect('wordbook_detail', pk=wordbook.pk)
    
    return render(request, 'home/wordbook_create.html')

# 単語帳詳細
@login_required
def wordbook_detail(request, pk):
    wordbook = get_object_or_404(WordBook, pk=pk)
    cards = wordbook.cards.all()
    
    likes_count = wordbook.likes.count()
    user_has_liked = wordbook.likes.filter(user=request.user).exists()
    
    context = {
        'likes_count': likes_count,
        'user_has_liked': user_has_liked,
        'wordbook': wordbook,
        'cards': cards,
    }
    return render(request, 'home/wordbook_detail.html', context)

# 単語カード作成
@login_required
def wordcard_create(request, wordbook_pk):
    wordbook = get_object_or_404(WordBook, pk=wordbook_pk, user=request.user)
    
    if request.method == 'POST':
        front_text = request.POST.get('front_text')
        back_text = request.POST.get('back_text')
        image = request.FILES.get('image')
        
        WordCard.objects.create(
            wordbook=wordbook,
            front_text=front_text,
            back_text=back_text,
            image=image
        )
        messages.success(request, '単語カードを追加しました!')
        return redirect('wordbook_detail', pk=wordbook.pk)
    
    context = {
        'wordbook': wordbook,
    }
    return render(request, 'home/wordcard_create.html', context)

# 単語カード削除
@login_required
def wordcard_delete(request, pk):
    card = get_object_or_404(WordCard, pk=pk)
    wordbook_pk = card.wordbook.pk
    
    if card.wordbook.user == request.user:
        card.delete()
        messages.success(request, '単語カードを削除しました')
    
    return redirect('wordbook_detail', pk=wordbook_pk)

#いいねトグル
@login_required
def wordbook_like_toggle(request, pk):
    wordbook = get_object_or_404(WordBook, pk=pk)
    next_url = request.POST.get('next') or reverse('wordbook_detail', args=[pk])
    if request.method == 'POST':
        like, created = wordBookLike.objects.get_or_create(user=request.user, wordbook=wordbook)
        if not created:
            like.delete()
    return redirect(next_url)   