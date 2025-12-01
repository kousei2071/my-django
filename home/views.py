from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db import models
from .models import WordBook, WordCard, UserProfile

# ホームページ（単語帳一覧）
def index(request):
    # 全ての単語帳を表示（認証不要）
    all_wordbooks = WordBook.objects.all()[:12]
    
    # ログインしている場合は自分の単語帳も表示
    my_wordbooks = None
    if request.user.is_authenticated:
        my_wordbooks = WordBook.objects.filter(user=request.user)
    
    context = {
        'all_wordbooks': all_wordbooks,
        'my_wordbooks': my_wordbooks,
    }
    return render(request, 'home/wordbook_list.html', context)

# ユーザー登録
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '会員登録が完了しました!')
            return redirect('home')
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
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'home/login.html', {'form': form})

# ログアウト
def logout_view(request):
    logout(request)
    messages.success(request, 'ログアウトしました')
    return redirect('home')

# マイページ（自分の単語帳管理）
@login_required
def my_wordbooks(request):
    # プロフィールがない場合は作成
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # 自分の単語帳のみ表示
    my_wordbooks = WordBook.objects.filter(user=request.user)
    
    # 合計カード数を計算
    total_cards = WordCard.objects.filter(wordbook__user=request.user).count()
    
    context = {
        'my_wordbooks': my_wordbooks,
        'total_cards': total_cards,
    }
    return render(request, 'home/my_wordbooks.html', context)

# プロフィール編集
@login_required
def profile_edit(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # プロフィール情報を更新
        profile.display_name = request.POST.get('display_name', '')
        profile.bio = request.POST.get('bio', '')
        
        # アバター画像の処理
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        messages.success(request, 'プロフィールを更新しました')
        return redirect('my_wordbooks')
    
    context = {
        'profile': profile,
    }
    return render(request, 'home/profile_edit.html', context)

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

# 単語帳詳細（認証不要で閲覧可能）
def wordbook_detail(request, pk):
    wordbook = get_object_or_404(WordBook, pk=pk)
    cards = wordbook.cards.all()
    
    # 編集権限の確認（作成者のみ）
    is_owner = request.user.is_authenticated and wordbook.user == request.user
    
    context = {
        'wordbook': wordbook,
        'cards': cards,
        'is_owner': is_owner,
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

# クイズ開始（認証不要）
def quiz_start(request, pk):
    wordbook = get_object_or_404(WordBook, pk=pk)
    cards = list(wordbook.cards.all())
    
    if len(cards) < 4:
        messages.error(request, 'クイズを開始するには最低4枚のカードが必要です。')
        return redirect('wordbook_detail', pk=pk)
    
    # URLパラメータから制限時間を取得（デフォルトは25秒）
    duration = int(request.GET.get('duration', 25))
    
    # セッションにカードIDと制限時間を保存
    request.session['quiz_cards'] = [card.id for card in cards]
    request.session['quiz_current'] = 0
    request.session['quiz_score'] = 0
    request.session['quiz_wordbook'] = pk
    request.session['quiz_duration'] = duration
    
    # 前回のクイズ結果をクリア
    if 'last_answer_result' in request.session:
        del request.session['last_answer_result']
    
    return redirect('quiz_question')

# クイズ問題表示（認証不要）
def quiz_question(request):
    import random
    import time
    import json
    
    # セッションから情報を取得
    card_ids = request.session.get('quiz_cards', [])
    current_index = request.session.get('quiz_current', 0)
    
    if not card_ids or current_index >= len(card_ids):
        return redirect('quiz_result')
    
    # 問題開始時刻を記録
    request.session['question_start_time'] = time.time()
    
    # 現在の問題カード
    current_card = get_object_or_404(WordCard, id=card_ids[current_index])
    
    # 選択肢の生成: まず同じ単語帳から取得
    same_wordbook_cards = list(
        WordCard.objects.filter(wordbook=current_card.wordbook)
        .exclude(id=current_card.id)
    )
    
    # 同じ単語帳から最大3つの誤答選択肢を取得
    if len(same_wordbook_cards) >= 3:
        wrong_choices = random.sample(same_wordbook_cards, 3)
    else:
        # 同じ単語帳内で足りない場合は、全て使用
        wrong_choices = same_wordbook_cards[:]
        
        # 足りない分を他の単語帳から補充
        needed = 3 - len(wrong_choices)
        if needed > 0:
            other_cards = list(
                WordCard.objects.exclude(wordbook=current_card.wordbook)
                .exclude(id=current_card.id)
            )
            if len(other_cards) >= needed:
                wrong_choices.extend(random.sample(other_cards, needed))
            else:
                wrong_choices.extend(other_cards)
    
    # 選択肢をシャッフル
    choices = [current_card] + wrong_choices
    random.shuffle(choices)
    
    # 前回の回答結果を取得
    last_result = request.session.get('last_answer_result', None)
    # 一度取得したらクリア
    if 'last_answer_result' in request.session:
        del request.session['last_answer_result']
    
    # JSONとして渡すために変換
    last_result_json = json.dumps(last_result) if last_result else 'null'
    
    # セッションから制限時間を取得（デフォルトは25秒）
    quiz_duration = request.session.get('quiz_duration', 25)
    
    context = {
        'question_card': current_card,
        'choices': choices,
        'current_number': current_index + 1,
        'total_questions': len(card_ids),
        'correct_answer_id': current_card.id,
        'last_result': last_result,  # 前回の結果を追加
        'last_result_json': last_result_json,  # JSON版も追加
        'quiz_duration': quiz_duration,  # 制限時間を追加
    }
    
    return render(request, 'home/quiz_question.html', context)

# クイズ回答処理（認証不要）
def quiz_answer(request):
    import time
    
    if request.method == 'POST':
        selected_id = int(request.POST.get('answer'))
        correct_id = int(request.POST.get('correct_answer'))
        correct_answer_text = request.POST.get('correct_answer_text', '')
        
        # 正解判定
        is_correct = selected_id == correct_id
        
        # 経過時間を計算
        start_time = request.session.get('question_start_time', time.time())
        elapsed_time = round(time.time() - start_time, 1)
        
        # 正解の単語情報を取得
        correct_card = get_object_or_404(WordCard, id=correct_id)
        
        # フロントエンドから渡された正解テキストを優先使用
        # 渡されていない場合はデータベースから取得
        if not correct_answer_text:
            correct_answer_text = correct_card.back_text
        
        # 結果情報をセッションに保存
        request.session['last_answer_result'] = {
            'is_correct': is_correct,
            'elapsed_time': elapsed_time,
            'correct_answer': correct_answer_text,  # 選択肢として表示されたテキストを使用
            'correct_word': correct_card.front_text,
        }
        
        if is_correct:
            request.session['quiz_score'] = request.session.get('quiz_score', 0) + 1
        
        # 次の問題へ
        request.session['quiz_current'] = request.session.get('quiz_current', 0) + 1
        
        return redirect('quiz_question')
    
    return redirect('quiz_question')

# クイズ結果表示（認証不要）
def quiz_result(request):
    score = request.session.get('quiz_score', 0)
    total = len(request.session.get('quiz_cards', []))
    wordbook_id = request.session.get('quiz_wordbook')
    
    # セッションをクリア
    for key in ['quiz_cards', 'quiz_current', 'quiz_score', 'quiz_wordbook']:
        if key in request.session:
            del request.session[key]
    
    wordbook = None
    if wordbook_id:
        wordbook = get_object_or_404(WordBook, pk=wordbook_id)
    
    context = {
        'score': score,
        'total': total,
        'percentage': round((score / total * 100) if total > 0 else 0, 1),
        'wordbook': wordbook,
    }
    
    return render(request, 'home/quiz_result.html', context)
