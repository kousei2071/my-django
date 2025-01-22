from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Count, Q
from django.urls import reverse
from django.http import JsonResponse, HttpResponseForbidden
from django.utils.text import slugify
from .models import WordBook, WordCard, Tag, wordBookLike, WordBookBookmark, UserProfile
import re

AVATAR_IMAGES = [
    'account.png',
    'account2.png',
    'account3.png',
    'account4.png',
    'account5.png',
    'account6.png',
]

BACKGROUND_COLORS = [
    '#fffff0',  # ivory
    '#e3d7a3',
    '#d8f3dc',
    '#f8d7da',
    '#dbeafe',
    '#fef3c7',
    '#e0f2fe',
]
# マイページ
@login_required
def mypage(request):
    # 自分の単語帳
    my_wordbooks_qs = WordBook.objects.filter(user=request.user).annotate(like_count=Count('likes')).order_by('-created_at')
    my_wordbooks_count = my_wordbooks_qs.count()
    my_wordbooks_preview = list(my_wordbooks_qs[:3])

    # 保存した単語帳（ブックマーク）
    bookmarked_qs = WordBook.objects.filter(bookmarks__user=request.user).annotate(like_count=Count('likes')).order_by('-bookmarks__created_at')
    saved_wordbooks_count = bookmarked_qs.count()
    saved_wordbooks_preview = list(bookmarked_qs[:6])

    nickname = request.user.first_name or request.user.username
    likes_total = wordBookLike.objects.filter(wordbook__user=request.user).count()
    
    # ユーザープロファイルを取得または作成
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'my_wordbooks': my_wordbooks_preview,
        'my_wordbooks_count': my_wordbooks_count,
        'saved_wordbooks': saved_wordbooks_preview,
        'saved_wordbooks_count': saved_wordbooks_count,
        'nickname': nickname,
        'likes_total': likes_total,
        'avatar_image': user_profile.avatar_image,
        'background_color': user_profile.background_color,
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
    # 検索パラメータを取得
    search_query = request.GET.get('q', '').strip()  # キーワード検索
    tag_name = request.GET.get('tag')  # タグ名での検索
    tag_ids = request.GET.get('tags')  # タグIDでの検索（複数対応）
    
    # 基本のクエリセット
    wordbooks_base = WordBook.objects.all()
    
    # キーワード検索
    if search_query:
        wordbooks_base = wordbooks_base.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(cards__front_text__icontains=search_query) |
            Q(cards__back_text__icontains=search_query)
        ).distinct()
    
    # タグでフィルタリング
    selected_tags = []
    if tag_name:
        # タグ名で検索（単一）
        wordbooks_base = wordbooks_base.filter(tags__name=tag_name).distinct()
        selected_tags = Tag.objects.filter(name=tag_name)
    elif tag_ids:
        # タグIDで検索（複数可能）
        tag_id_list = [int(x) for x in tag_ids.split(',') if x.strip().isdigit()]
        wordbooks_base = wordbooks_base.filter(tags__id__in=tag_id_list).distinct()
        selected_tags = Tag.objects.filter(id__in=tag_id_list)
    
    # 人気の単語帳（いいね数順）
    popular_wordbooks = wordbooks_base.annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')[:6]
    
    # 既存の単語帳（新着順、ログインユーザーが作成したもののみ）
    if request.user.is_authenticated:
        existing_wordbooks = WordBook.objects.filter(user=request.user).annotate(like_count=Count('likes')).order_by('-created_at')[:6]
    else:
        existing_wordbooks = []
    
    # 人気タグTOP10を取得（使用数順）
    popular_tags = Tag.objects.annotate(
        usage_count=Count('wordbooks')
    ).filter(usage_count__gt=0).order_by('-usage_count', 'name')[:10]
    
    # 選択中のタグ名のリストを作成
    selected_tag_names = [tag.name for tag in selected_tags]
    
    context = {
        'popular_wordbooks': popular_wordbooks,
        'existing_wordbooks': existing_wordbooks,
        'popular_tags': popular_tags,  # 人気タグを追加
        'search_query': search_query,  # 検索クエリを追加
        'selected_tags': selected_tags,  # 選択中のタグ
        'selected_tag_names': selected_tag_names,  # 選択中のタグ名リスト
        'is_filtered': bool(tag_name or tag_ids or search_query),  # フィルター中かどうか
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
    user_has_bookmarked = wordbook.bookmarks.filter(user=request.user).exists()
    # 所有者なら常に編集ボタン（カード追加など）を表示
    can_edit = wordbook.user == request.user
    
    context = {
        'likes_count': likes_count,
        'user_has_liked': user_has_liked,
        'user_has_bookmarked': user_has_bookmarked,
        'can_edit': can_edit,
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
        
        WordCard.objects.create(
            wordbook=wordbook,
            front_text=front_text,
            back_text=back_text
        )
        messages.success(request, '単語カードを追加しました。続けて追加できます。')
        return redirect('wordcard_create', wordbook_pk=wordbook.pk)
    
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


# ブックマークトグル
@login_required
def wordbook_bookmark_toggle(request, pk):
    wordbook = get_object_or_404(WordBook, pk=pk)
    next_url = request.POST.get('next') or reverse('wordbook_detail', args=[pk])
    if request.method == 'POST':
        bookmark, created = WordBookBookmark.objects.get_or_create(user=request.user, wordbook=wordbook)
        if not created:
            bookmark.delete()
    return redirect(next_url)


# ---- Tag APIs ----
def _normalize_tag_name(name: str) -> str:
    # 先頭の#除去、trim、連続空白を1つに
    if not name:
        return ''
    s = name.strip()
    if s.startswith('#'):
        s = s[1:]
    s = re.sub(r"\s+", " ", s)
    return s


def tags_list(request):
    q = (request.GET.get('q') or '').strip()
    try:
        limit = int(request.GET.get('limit') or 20)
        offset = int(request.GET.get('offset') or 0)
    except ValueError:
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'limit/offset must be integers'}}, status=400)
    order_by = request.GET.get('order_by') or 'name'
    if limit < 1 or limit > 50 or offset < 0 or order_by not in ('name', '-name'):
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'invalid limit/offset/order_by'}}, status=400)

    qs = Tag.objects.all()
    if q:
        qs = qs.filter(name__icontains=q)
    total = qs.count()
    items = qs.order_by(order_by)[offset:offset+limit]
    # usage_countは必要に応じて別クエリで集計可能。ここでは省略/0固定にせず関連数を取得
    user_id = request.user.id if request.user.is_authenticated else None
    payload = [
        {
            'id': t.id,
            'name': t.name,
            'slug': t.slug,
            'usage_count': t.wordbooks.count(),
            'created_by_me': t.created_by_id == user_id if user_id else False,
        } for t in items
    ]
    next_url = None
    prev_url = None
    if offset + limit < total:
        next_url = f"?q={q}&limit={limit}&offset={offset+limit}&order_by={order_by}"
    if offset > 0:
        prev_off = max(0, offset - limit)
        prev_url = f"?q={q}&limit={limit}&offset={prev_off}&order_by={order_by}"
    return JsonResponse({'tags': payload, 'count': total, 'next': next_url, 'prev': prev_url})


from django.contrib.auth.decorators import login_required


@login_required
def tag_create(request):
    if request.method != 'POST':
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'POST required'}}, status=400)
    raw = request.POST.get('name')
    name = _normalize_tag_name(raw or '')
    if not name:
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'name required'}}, status=400)
    if len(name) > 50:
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'name too long'}}, status=400)
    slug = slugify(name, allow_unicode=True)[:60]
    if not slug:
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'invalid name'}}, status=400)
    tag, created = Tag.objects.get_or_create(slug=slug, defaults={'name': name, 'created_by': request.user})
    return JsonResponse({'id': tag.id, 'name': tag.name, 'slug': tag.slug, 'created': created}, status=201 if created else 200)


@login_required
def tag_delete(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    if tag.created_by != request.user:
        return HttpResponseForbidden('not allowed')
    if request.method != 'POST':
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'POST required'}}, status=400)
    
    # 使用されているかチェック
    if tag.wordbooks.exists():
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'tag is in use'}}, status=400)
    
    tag.delete()
    return JsonResponse({'ok': True})


@login_required
def wordbook_update_tags(request, pk):
    wb = get_object_or_404(WordBook, pk=pk)
    if wb.user != request.user:
        return HttpResponseForbidden('not allowed')
    if request.method != 'POST':
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'POST required'}}, status=400)

    tag_ids_raw = (request.POST.get('tag_ids') or '').strip()
    tag_slugs_raw = (request.POST.get('tag_slugs') or '').strip()

    ids = []
    slugs = []
    if tag_ids_raw:
        try:
            ids = [int(x) for x in tag_ids_raw.split(',') if x.strip()]
        except ValueError:
            return JsonResponse({'error': {'code': 'BadRequest', 'message': 'invalid tag_ids'}}, status=400)
    if tag_slugs_raw:
        slugs = [x.strip() for x in tag_slugs_raw.split(',') if x.strip()]

    if len(ids) + len(slugs) > 10:
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'too many tags (max 10)'}}, status=400)

    tags = Tag.objects.filter(Q(id__in=ids) | Q(slug__in=slugs))
    if tags.count() != len(set(ids)) + len(set(slugs)) and (ids or slugs):
        # 一部見つからない場合は400（緩和するならここは警告に変更可）
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'some tags not found'}}, status=400)

    wb.tags.set(tags)
    return JsonResponse({'ok': True, 'tag_ids': [t.id for t in tags]})


# 自分の単語帳全件
@login_required
def my_wordbooks_all(request):
    my_wordbooks_qs = WordBook.objects.filter(user=request.user).annotate(like_count=Count('likes')).order_by('-created_at')
    context = {
        'title': '自分の単語帳',
        'wordbooks': my_wordbooks_qs,
        'from_source': 'mypage',
    }
    return render(request, 'home/wordbook_collection_full.html', context)


# ブックマーク全件
@login_required
def bookmarked_wordbooks_all(request):
    bookmarked_qs = WordBook.objects.filter(bookmarks__user=request.user).annotate(like_count=Count('likes')).order_by('-bookmarks__created_at')
    context = {
        'title': '保存した単語帳',
        'wordbooks': bookmarked_qs,
        'from_source': 'bookmarks',
    }
    return render(request, 'home/wordbook_collection_full.html', context)


# ---- Avatar APIs ----
@login_required
def get_available_avatars(request):
    """利用可能なアバター画像一覧を返す"""
    return JsonResponse({'avatars': AVATAR_IMAGES})


@login_required
def get_available_backgrounds(request):
    """利用可能なアバター背景色一覧を返す"""
    return JsonResponse({'backgrounds': BACKGROUND_COLORS})


@login_required
def update_avatar(request):
    """ユーザーのアバター画像を更新"""
    if request.method != 'POST':
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'POST required'}}, status=400)
    
    avatar_image = request.POST.get('avatar_image', '').strip()
    if avatar_image not in AVATAR_IMAGES:
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'invalid avatar image'}}, status=400)
    
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_profile.avatar_image = avatar_image
    user_profile.save()
    return JsonResponse({'ok': True, 'avatar_image': user_profile.avatar_image})


@login_required
def update_background(request):
    """ユーザーのアバター背景色を更新"""
    if request.method != 'POST':
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'POST required'}}, status=400)

    background_color = request.POST.get('background_color', '').strip().lower()
    if background_color not in [c.lower() for c in BACKGROUND_COLORS]:
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'invalid background color'}}, status=400)

    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_profile.background_color = background_color
    user_profile.save()
    return JsonResponse({'ok': True, 'background_color': user_profile.background_color})