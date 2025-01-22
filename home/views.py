from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q
from django.urls import reverse
from django.http import JsonResponse, HttpResponseForbidden, Http404
from django.utils.text import slugify
from .models import WordBook, WordCard, Tag, wordBookLike, WordBookBookmark, UserProfile, WordCardStar
import re
import random
import json

AVATAR_IMAGES = [
    'account.png',
    'account2.png',
    'account3.png',
    'account4.png',
    'account5.png',
    'account6.png',
    'account7.png',
    'account8.png',
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


def user_can_view_wordbook(wordbook, user):
    """公開済み、AI生成、作成者、または管理者のみ閲覧可"""
    if wordbook.is_ai_generated:
        return True
    if wordbook.is_public:
        return True
    if not user.is_authenticated:
        return False
    return wordbook.user == user or is_admin_user(user)


def get_wordbook_for_view(pk, user):
    """閲覧できる単語帳のみ取得し、存在しない扱いにする"""
    if user.is_authenticated and is_admin_user(user):
        qs = WordBook.objects.all()
    elif user.is_authenticated:
        qs = WordBook.objects.filter(Q(is_public=True) | Q(is_ai_generated=True) | Q(user=user))
    else:
        qs = WordBook.objects.filter(Q(is_public=True) | Q(is_ai_generated=True))
    return get_object_or_404(qs, pk=pk)
# マイページ
@login_required
def mypage(request):
    # 自分の単語帳
    my_wordbooks_qs = WordBook.objects.filter(user=request.user).annotate(like_count=Count('likes')).order_by('-created_at')
    my_wordbooks_count = my_wordbooks_qs.count()
    my_wordbooks_preview = list(my_wordbooks_qs[:3])

    # 保存した単語帳（ブックマーク）
    bookmarked_qs = WordBook.objects.filter(bookmarks__user=request.user).filter(Q(is_public=True) | Q(user=request.user)).annotate(like_count=Count('likes')).order_by('-bookmarks__created_at')
    saved_wordbooks_count = bookmarked_qs.count()
    saved_wordbooks_preview = list(bookmarked_qs[:6])

    nickname = request.user.first_name or request.user.username
    likes_total = wordBookLike.objects.filter(wordbook__user=request.user).count()
    starred_cards_count = WordCardStar.objects.filter(user=request.user).count()
    
    # ユーザープロファイルを取得または作成
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'my_wordbooks': my_wordbooks_preview,
        'my_wordbooks_count': my_wordbooks_count,
        'saved_wordbooks': saved_wordbooks_preview,
        'saved_wordbooks_count': saved_wordbooks_count,
        'nickname': nickname,
        'likes_total': likes_total,
        'starred_cards_count': starred_cards_count,
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
    
    # 基本のクエリセット（index では非公開は出さない。AIは常に表示）
    if request.user.is_authenticated and is_admin_user(request.user):
        wordbooks_base = WordBook.objects.all()
    else:
        wordbooks_base = WordBook.objects.filter(Q(is_public=True) | Q(is_ai_generated=True))
    
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
    
    # ピン留めされた単語帳（管理者のおすすめ）
    pinned_wordbooks = wordbooks_base.filter(is_pinned=True, is_public=True).annotate(like_count=Count('likes')).order_by('-created_at')[:6]
    
    # 人気の単語帳（いいね数順）: フィルター中は絞り込み結果のみ、未フィルター時も公開/AIのみ
    public_ai = WordBook.objects.filter(Q(is_public=True) | Q(is_ai_generated=True))
    popular_source = wordbooks_base if (tag_name or tag_ids or search_query) else public_ai
    popular_wordbooks = popular_source.annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')[:6]
    
    # AIの単語帳: フィルター中は絞り込み結果のみ、未フィルター時も公開/AIのみ
    ai_source = wordbooks_base if (tag_name or tag_ids or search_query) else public_ai
    ai_wordbooks = ai_source.filter(is_ai_generated=True).annotate(like_count=Count('likes')).order_by('-created_at')[:12]
    
    # 人気タグTOP10を取得（使用数順）
    popular_tags = Tag.objects.annotate(
        usage_count=Count('wordbooks')
    ).filter(usage_count__gt=0).order_by('-usage_count', 'name')[:10]
    
    # 選択中のタグ名のリストを作成
    selected_tag_names = [tag.name for tag in selected_tags]
    
    # 管理者かどうかをチェック
    is_admin = is_admin_user(request.user) if request.user.is_authenticated else False
    
    context = {
        'pinned_wordbooks': pinned_wordbooks,  # ピン留め単語帳を追加
        'popular_wordbooks': popular_wordbooks,
        'ai_wordbooks': ai_wordbooks,
        'popular_tags': popular_tags,  # 人気タグを追加
        'search_query': search_query,  # 検索クエリを追加
        'selected_tags': selected_tags,  # 選択中のタグ
        'selected_tag_names': selected_tag_names,  # 選択中のタグ名リスト
        'is_filtered': bool(tag_name or tag_ids or search_query),  # フィルター中かどうか
        'is_admin': is_admin,  # 管理者権限
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
    wordbook = get_wordbook_for_view(pk, request.user)
    cards = wordbook.cards.all()
    
    likes_count = wordbook.likes.count()
    user_has_liked = False
    user_has_bookmarked = False
    starred_card_ids = []
    
    if request.user.is_authenticated:
        user_has_liked = wordbook.likes.filter(user=request.user).exists()
        user_has_bookmarked = wordbook.bookmarks.filter(user=request.user).exists()
        starred_card_ids = list(WordCardStar.objects.filter(user=request.user, wordcard__in=cards).values_list('wordcard_id', flat=True))
    
    # 所有者なら常に編集ボタン（カード追加など）を表示
    can_edit = wordbook.user == request.user if request.user.is_authenticated else False
    
    context = {
        'likes_count': likes_count,
        'user_has_liked': user_has_liked,
        'user_has_bookmarked': user_has_bookmarked,
        'starred_card_ids': starred_card_ids,
        'can_edit': can_edit,
        'wordbook': wordbook,
        'cards': cards,
    }
    return render(request, 'home/wordbook_detail.html', context)


@login_required
def wordbook_play(request, pk):
    wordbook = get_wordbook_for_view(pk, request.user)
    cards = list(wordbook.cards.all())

    if len(cards) < 4:
        messages.error(request, 'プレイするにはカードが4枚以上必要です')
        return redirect('wordbook_detail', pk=pk)

    cards_data = [
        {
            'id': c.id,
            'front': c.front_text,
            'back': c.back_text,
        }
        for c in cards
    ]

    context = {
        'wordbook': wordbook,
        'cards_json': json.dumps(cards_data, ensure_ascii=False),
        'card_count': len(cards),
    }
    return render(request, 'home/wordbook_play.html', context)

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
    
    starred_cards = WordCardStar.objects.filter(user=request.user).select_related('wordcard')
    
    context = {
        'wordbook': wordbook,
        'starred_cards': starred_cards,
    }
    return render(request, 'home/wordcard_create.html', context)

@login_required
def import_starred_card(request, wordbook_pk, card_id):
    wordbook = get_object_or_404(WordBook, pk=wordbook_pk, user=request.user)
    original_card = get_object_or_404(WordCard, id=card_id)

    if not user_can_view_wordbook(original_card.wordbook, request.user):
        raise Http404()
    
    # 星をつけているか確認
    if not WordCardStar.objects.filter(user=request.user, wordcard=original_card).exists():
        raise Http404()
        
    # コピーを作成
    WordCard.objects.create(
        wordbook=wordbook,
        front_text=original_card.front_text,
        back_text=original_card.back_text,
        image=original_card.image
    )
    
    messages.success(request, f'「{original_card.front_text}」をインポートしました。')
    return redirect('wordcard_create', wordbook_pk=wordbook_pk)

# 単語カード削除
@login_required
def wordcard_delete(request, pk):
    card = get_object_or_404(WordCard, pk=pk)
    wordbook_pk = card.wordbook.pk
    
    if card.wordbook.user == request.user:
        card.delete()
        messages.success(request, '単語カードを削除しました')
    
    return redirect('wordbook_detail', pk=wordbook_pk)

# いいねトグル
@login_required
def wordbook_like_toggle(request, pk):
    wordbook = get_wordbook_for_view(pk, request.user)
    next_url = request.POST.get('next') or reverse('wordbook_detail', args=[pk])
    if request.method == 'POST':
        like, created = wordBookLike.objects.get_or_create(user=request.user, wordbook=wordbook)
        if not created:
            like.delete()
    return redirect(next_url)   


# ブックマークトグル
@login_required
def wordbook_bookmark_toggle(request, pk):
    wordbook = get_wordbook_for_view(pk, request.user)
    next_url = request.POST.get('next') or reverse('wordbook_detail', args=[pk])
    if request.method == 'POST':
        bookmark, created = WordBookBookmark.objects.get_or_create(user=request.user, wordbook=wordbook)
        if not created:
            bookmark.delete()
    return redirect(next_url)


@login_required
def wordbook_toggle_public(request, pk):
    wordbook = get_object_or_404(WordBook, pk=pk, user=request.user)
    if request.method != 'POST':
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'POST required'}}, status=400)

    action = request.POST.get('action')
    if action == 'publish':
        wordbook.is_public = True
        message = '単語帳を公開しました'
    elif action == 'unpublish':
        wordbook.is_public = False
        message = '単語帳を非公開にしました'
    else:
        wordbook.is_public = not wordbook.is_public
        message = '公開設定を更新しました'

    wordbook.save(update_fields=['is_public'])
    messages.success(request, message)

    next_url = request.POST.get('next') or reverse('wordbook_detail', args=[pk])
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
    bookmarked_qs = WordBook.objects.filter(bookmarks__user=request.user).filter(Q(is_public=True) | Q(user=request.user)).annotate(like_count=Count('likes')).order_by('-bookmarks__created_at')
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
    
    # プリセット画像が選択された場合、カスタムアバターをクリアする
    if user_profile.custom_avatar:
        user_profile.custom_avatar.delete()
        user_profile.custom_avatar = None
        
    user_profile.save()
    return JsonResponse({'ok': True, 'avatar_image': user_profile.avatar_image, 'avatar_url': user_profile.get_avatar_url()})


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


@login_required
def upload_custom_avatar(request):
    """カスタムアバター画像をアップロード"""
    if request.method != 'POST':
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'POST required'}}, status=400)
    
    if 'avatar_file' not in request.FILES:
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'No file provided'}}, status=400)
    
    file = request.FILES['avatar_file']
    
    # ファイルタイプチェック
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'Invalid file type. Only images are allowed'}}, status=400)
    
    # ファイルサイズチェック（5MB制限）
    if file.size > 5 * 1024 * 1024:
        return JsonResponse({'error': {'code': 'BadRequest', 'message': 'File too large. Max 5MB'}}, status=400)
    
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # 既存のカスタムアバターがある場合は削除
    if user_profile.custom_avatar:
        user_profile.custom_avatar.delete()
    
    # 新しいアバターを保存
    user_profile.custom_avatar = file
    user_profile.save()
    
    return JsonResponse({
        'ok': True,
        'avatar_url': user_profile.get_avatar_url()
    })
@login_required
def toggle_star(request, card_id):
    card = get_object_or_404(WordCard, id=card_id)
    if not user_can_view_wordbook(card.wordbook, request.user):
        raise Http404()
    star, created = WordCardStar.objects.get_or_create(user=request.user, wordcard=card)
    
    if not created:
        star.delete()
        is_starred = False
    else:
        is_starred = True
        
    return JsonResponse({'is_starred': is_starred})


# ==================== 管理者専用機能 ====================
def is_admin_user(user):
    """sakana kousei1207かどうかをチェック"""
    return user.username == 'sakana' and user.first_name == 'kousei1207'

@login_required
def admin_dashboard(request):
    """管理者専用ダッシュボード"""
    if not is_admin_user(request.user):
        return HttpResponseForbidden("この機能は管理者専用です。")
    
    # 統計情報を収集
    total_users = User.objects.count()
    total_wordbooks = WordBook.objects.count()
    total_wordcards = WordCard.objects.count()
    total_likes = wordBookLike.objects.count()
    total_bookmarks = WordBookBookmark.objects.count()
    
    # 人気の単語帳TOP10
    popular_wordbooks = WordBook.objects.annotate(
        like_count=Count('likes')
    ).order_by('-like_count')[:10]
    
    # 最近作成された単語帳
    recent_wordbooks = WordBook.objects.select_related('user').order_by('-created_at')[:10]
    
    # アクティブユーザーTOP10（単語帳作成数）
    active_users = User.objects.annotate(
        wordbook_count=Count('wordbooks')
    ).filter(wordbook_count__gt=0).order_by('-wordbook_count')[:10]
    
    # タグ使用統計
    tag_stats = Tag.objects.annotate(
        usage_count=Count('wordbooks')
    ).filter(usage_count__gt=0).order_by('-usage_count')[:10]
    
    # ピン留めされた単語帳
    pinned_wordbooks = WordBook.objects.filter(is_pinned=True).annotate(
        like_count=Count('likes')
    ).order_by('-created_at')
    
    context = {
        'total_users': total_users,
        'total_wordbooks': total_wordbooks,
        'total_wordcards': total_wordcards,
        'total_likes': total_likes,
        'total_bookmarks': total_bookmarks,
        'popular_wordbooks': popular_wordbooks,
        'recent_wordbooks': recent_wordbooks,
        'active_users': active_users,
        'tag_stats': tag_stats,
        'pinned_wordbooks': pinned_wordbooks,
    }
    
    return render(request, 'home/admin_dashboard.html', context)


@login_required
def admin_delete_wordbook(request, pk):
    """管理者専用：単語帳を削除（BAN機能）"""
    if not is_admin_user(request.user):
        return HttpResponseForbidden("この機能は管理者専用です。")
    
    wordbook = get_object_or_404(WordBook, pk=pk)
    
    if request.method == 'POST':
        title = wordbook.title
        wordbook.delete()
        messages.success(request, f'単語帳「{title}」を削除しました。')
        return redirect('admin_dashboard')
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def admin_toggle_pin(request, pk):
    """管理者専用：単語帳のピン留めをトグル"""
    if not is_admin_user(request.user):
        return JsonResponse({'error': '権限がありません'}, status=403)
    
    wordbook = get_object_or_404(WordBook, pk=pk)
    wordbook.is_pinned = not wordbook.is_pinned
    wordbook.save()
    
    return JsonResponse({
        'success': True,
        'is_pinned': wordbook.is_pinned
    })
