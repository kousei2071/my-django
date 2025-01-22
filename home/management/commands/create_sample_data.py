from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from home.models import WordBook, WordCard, Tag
from django.utils.text import slugify
import random

class Command(BaseCommand):
    help = 'Create sample wordbooks and wordcards'

    def handle(self, *args, **options):
        AVATAR_IMAGES = [
            'account.png', 'account2.png', 'account3.png', 'account4.png',
            'account5.png', 'account6.png', 'account7.png', 'account8.png',
        ]

        BACKGROUND_COLORS = [
            '#fffff0', '#e3d7a3', '#d8f3dc', '#f8d7da', '#dbeafe', '#fef3c7', '#e0f2fe',
        ]

        # 既定タグ
        default_tags = [
            {'name': '英検3級', 'slug': 'eiken-3kyu'},
            {'name': '英検準2級', 'slug': 'eiken-jun2'},
            {'name': '英検2級', 'slug': 'eiken-2kyu'},
            {'name': '英検準1級', 'slug': 'eiken-jun1'},
            {'name': 'TOEIC600', 'slug': 'toeic-600'},
            {'name': 'TOEIC800', 'slug': 'toeic-800'},
            {'name': 'TOEIC900', 'slug': 'toeic-900'},
            {'name': '大学受験', 'slug': 'university-exam'},
            {'name': '高校受験', 'slug': 'high-school-exam'},
            {'name': '中学英語', 'slug': 'junior-high'},
            {'name': '日常会話', 'slug': 'daily-conversation'},
            {'name': 'ビジネス英語', 'slug': 'business-english'},
            {'name': '旅行英語', 'slug': 'travel-english'},
            {'name': 'IT用語', 'slug': 'it-terms'},
            {'name': '医療英語', 'slug': 'medical-english'},
            {'name': '基礎', 'slug': 'basic'},
            {'name': '初級', 'slug': 'beginner'},
            {'name': '中級', 'slug': 'intermediate'},
            {'name': '上級', 'slug': 'advanced'},
            {'name': '単語', 'slug': 'vocabulary'},
            {'name': '熟語', 'slug': 'idioms'},
            {'name': '文法', 'slug': 'grammar'},
            
        ]
        for item in default_tags:
            Tag.objects.get_or_create(name=item['name'], defaults={
                'slug': item['slug']
            })

        # サンプルユーザーを作成（既に存在する場合はスキップ）
        sample_users = []
        for i in range(1, 6):
            username = f'sample_user_{i}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'user{i}@example.com',
                    'first_name': f'Sample{i}',
                    'last_name': 'User'
                }
            )
            if created:
                user.set_password('samplepass123')
                user.save()
                self.stdout.write(f'Created user: {username}')
            sample_users.append(user)

        # 既存のサンプル単語帳を削除（作り直しのリクエストに対応）
        self.stdout.write('Deleting existing sample wordbooks...')
        WordBook.objects.filter(user__username__startswith='sample_user_').delete()

        # サンプル単語帳データ
        wordbooks_data = [
            {
                'title': 'TOEIC必須単語 600点レベル',
                'description': 'TOEIC 600点を目指すための基本的な英単語集です。ビジネスシーンでよく使われる単語を中心に収録しています。',
                'tags': ['TOEIC600', 'ビジネス英語', '単語'],
                'cards': [
                    ('accomplish', '達成する、成し遂げる'),
                    ('acquire', '取得する、習得する'),
                    ('adequate', '適切な、十分な'),
                    ('administrative', '管理の、運営の'),
                    ('announce', '発表する、告知する'),
                    ('appointment', '予約、約束、任命'),
                    ('approve', '承認する、賛成する'),
                    ('approximately', 'およそ、約'),
                    ('arrangement', '手配、配置、取り決め'),
                    ('attend', '出席する、参加する'),
                ]
            },
            {
                'title': '大学受験英単語 基礎編',
                'description': '大学受験に必要な基礎的な英単語を厳選しました。まずはこれらの単語をしっかりと覚えましょう。',
                'tags': ['大学受験', '基礎', '単語'],
                'cards': [
                    ('ability', '能力、才能'),
                    ('accept', '受け入れる、認める'),
                    ('access', 'アクセス、接近'),
                    ('accident', '事故、偶然'),
                    ('account', '口座、説明、理由'),
                    ('accurate', '正確な、精密な'),
                    ('achieve', '達成する、成し遂げる'),
                    ('action', '行動、動作'),
                    ('active', '活発な、積極的な'),
                    ('actual', '実際の、現実の'),
                ]
            },
            {
                'title': '日常英会話 頻出フレーズ',
                'description': '日常会話で使える基本的な英語フレーズ集。覚えておくと便利な表現ばかりです。',
                'tags': ['日常会話', '初級', '文法'],
                'cards': [
                    ("How's it going?", '調子はどう？'),
                    ("What's up?", '元気？何してる？'),
                    ("I'm fine, thank you", 'おかげさまで元気です'),
                    ("Nice to meet you", 'はじめまして'),
                    ("See you later", 'また後でね'),
                    ("Take care", '気をつけて'),
                    ("Good luck", '幸運を祈ります'),
                    ("You're welcome", 'どういたしまして'),
                    ("I'm sorry", 'すみません'),
                    ("Excuse me", 'すみません（通してください）'),
                ]
            },
            {
                'title': 'IT・プログラミング英単語',
                'description': 'プログラミングやIT分野でよく使われる英単語集。エンジニアを目指す方におすすめです。',
                'tags': ['IT用語', '上級', '単語'],
                'cards': [
                    ('algorithm', 'アルゴリズム、計算手法'),
                    ('application', 'アプリケーション、応用'),
                    ('authentication', '認証、本人確認'),
                    ('backup', 'バックアップ、予備'),
                    ('database', 'データベース'),
                    ('debug', 'デバッグ、不具合修正'),
                    ('deploy', '配置する、展開する'),
                    ('framework', 'フレームワーク、枠組み'),
                    ('interface', 'インターフェース、接点'),
                    ('repository', 'リポジトリ、貯蔵庫'),
                ]
            },
            {
                'title': '英検2級 重要単語',
                'description': '英検2級合格のために覚えておきたい重要単語を集めました。高校レベルの語彙力向上に最適です。',
                'tags': ['英検2級', '中級', '単語'],
                'cards': [
                    ('advance', '前進する、進歩'),
                    ('advantage', '利点、有利'),
                    ('agricultural', '農業の'),
                    ('ancient', '古代の、古い'),
                    ('anxiety', '不安、心配'),
                    ('appearance', '外見、出現'),
                    ('appreciate', '感謝する、理解する'),
                    ('argument', '議論、論争'),
                    ('ArticleKey', '記事、品物'),
                    ('atmosphere', '雰囲気、大気'),
                ]
            },
            {
                'title': '旅行英会話 基本フレーズ',
                'description': '海外旅行で役立つ基本的な英会話フレーズ。空港、ホテル、レストランなどで使える表現を収録しています。',
                'tags': ['旅行英語', '初級', '日常会話'],
                'cards': [
                    ('Where is the bathroom?', 'トイレはどこですか？'),
                    ('How much is this?', 'これはいくらですか？'),
                    ('Can I have the menu?', 'メニューをください'),
                    ('I would like to check in', 'チェックインをお願いします'),
                    ('Do you have Wi-Fi?', 'Wi-Fiはありますか？'),
                    ('Can you recommend something?', '何かおすすめはありますか？'),
                    ('I need help', '助けが必要です'),
                    ('Where can I buy tickets?', 'チケットはどこで買えますか？'),
                    ('Is there a pharmacy nearby?', '近くに薬局はありますか？'),
                    ('Thank you for your help', 'ご協力ありがとうございます'),
                ]
            },
            {
                'title': '中学英語 基礎動詞',
                'description': '中学英語で学ぶ基本的な動詞を集めました。英語学習の土台となる重要な単語ばかりです。',
                'tags': ['中学英語', '基礎', '単語'],
                'cards': [
                    ('be', 'である、いる'),
                    ('have', '持っている'),
                    ('do', 'する、行う'),
                    ('make', '作る、させる'),
                    ('get', '得る、手に入れる'),
                    ('take', '取る、持っていく'),
                    ('go', '行く'),
                    ('come', '来る'),
                    ('see', '見る'),
                    ('know', '知っている'),
                ]
            },
            {
                'title': 'TOEIC800点レベル 必須単語',
                'description': 'TOEIC800点を目指すための中上級単語集。ビジネス文書でよく使われる表現を収録しています。',
                'tags': ['TOEIC800', 'ビジネス英語', '中級'],
                'cards': [
                    ('accommodate', '収容する、適応させる'),
                    ('accomplish', '達成する、完成させる'),
                    ('accumulate', '蓄積する、集める'),
                    ('adjacent', '隣接した、近接の'),
                    ('administer', '管理する、運営する'),
                    ('allocate', '割り当てる、配分する'),
                    ('anticipate', '予期する、期待する'),
                    ('assess', '評価する、査定する'),
                    ('authorize', '権限を与える、認可する'),
                    ('comprehend', '理解する、把握する'),
                ]
            },
            {
                'title': '英検準1級 頻出単語',
                'description': '英検準1級に頻出する単語を厳選。大学上級レベルの語彙力を身につけることができます。',
                'tags': ['英検準1級', '上級', '単語'],
                'cards': [
                    ('abolish', '廃止する'),
                    ('abstract', '抽象的な、要約'),
                    ('accountable', '説明責任のある'),
                    ('accumulate', '蓄積する'),
                    ('acknowledge', '認める、承認する'),
                    ('advocate', '提唱する、支持者'),
                    ('affluent', '裕福な、豊かな'),
                    ('aggregate', '集合、総計'),
                    ('aggressive', '攻撃的な、積極的な'),
                    ('allocate', '割り当てる'),
                ]
            },
            {
                'title': 'ビジネスメール 定型表現',
                'description': 'ビジネスメールで使える定型表現集。丁寧な英語表現を身につけることができます。',
                'tags': ['ビジネス英語', '中級', '文法'],
                'cards': [
                    ('I am writing to inquire about', '～についてお問い合わせいたします'),
                    ('Thank you for your prompt reply', '迅速なご返信ありがとうございます'),
                    ('I would appreciate it if you could', '～していただければ幸いです'),
                    ('Please let me know if you have any questions', 'ご質問がございましたらお知らせください'),
                    ('I look forward to hearing from you', 'お返事をお待ちしております'),
                    ('Please find attached', '添付ファイルをご確認ください'),
                    ('I apologize for the inconvenience', 'ご不便をおかけして申し訳ございません'),
                    ('Could you please provide', '～をご提供いただけますでしょうか'),
                    ('We would like to inform you that', '～についてお知らせいたします'),
                    ('Best regards', '敬具、よろしくお願いいたします'),
                ]
            },
            {
                'title': 'AI・機械学習 英単語',
                'description': '人工知能や機械学習分野で頻出する英単語集。AI技術を学ぶ方に必須の用語を収録しています。',
                'tags': ['IT用語', '上級', '単語'],
                'cards': [
                    ('artificial intelligence', '人工知能'),
                    ('machine learning', '機械学習'),
                    ('neural network', 'ニューラルネットワーク、神経回路網'),
                    ('deep learning', 'ディープラーニング、深層学習'),
                    ('dataset', 'データセット'),
                    ('model', 'モデル、模型'),
                    ('training', '訓練、学習'),
                    ('accuracy', '精度、正確度'),
                    ('prediction', '予測'),
                    ('algorithm', 'アルゴリズム'),
                ]
            },
            {
                'title': '医療英語 基本単語',
                'description': '医療現場で使われる基本的な英単語集。医療従事者や医学部生におすすめです。',
                'tags': ['医療英語', '中級', '単語'],
                'cards': [
                    ('symptom', '症状'),
                    ('diagnosis', '診断'),
                    ('treatment', '治療、処置'),
                    ('prescription', '処方箋'),
                    ('medication', '薬、投薬'),
                    ('surgery', '手術'),
                    ('patient', '患者'),
                    ('physician', '医師'),
                    ('nurse', '看護師'),
                    ('examination', '検査、診察'),
                ]
            },
            {
                'title': '英検3級 基礎単語',
                'description': '英検3級合格に必要な基礎単語集。中学卒業レベルの語彙力を身につけることができます。',
                'tags': ['英検3級', '基礎', '単語'],
                'cards': [
                    ('answer', '答える、答え'),
                    ('ask', '尋ねる、頼む'),
                    ('become', 'になる'),
                    ('begin', '始まる、始める'),
                    ('believe', '信じる、思う'),
                    ('between', 'の間に'),
                    ('both', '両方の'),
                    ('bring', '持ってくる'),
                    ('build', '建てる、作る'),
                    ('business', '仕事、商売、企業'),
                ]
            },
            {
                'title': 'TOEIC900点レベル 上級単語',
                'description': 'TOEIC900点以上を目指すための高度な単語集。ビジネス上級レベルの語彙力を養えます。',
                'tags': ['TOEIC900', '上級', 'ビジネス英語'],
                'cards': [
                    ('comprehensive', '包括的な、総合的な'),
                    ('crucial', '重要な、決定的な'),
                    ('demonstrate', '実証する、示す'),
                    ('deteriorate', '悪化する'),
                    ('efficient', '効率的な'),
                    ('emphasize', '強調する'),
                    ('facilitate', '容易にする、促進する'),
                    ('implement', '実施する、実行する'),
                    ('initiative', 'イニシアチブ、主導権'),
                    ('innovative', '革新的な'),
                ]
            },
            {
                'title': '高校受験 頻出英単語',
                'description': '高校受験に頻出する重要英単語集。公立・私立高校入試に対応した内容です。',
                'tags': ['高校受験', '中学英語', '単語'],
                'cards': [
                    ('almost', 'ほとんど、もう少しで'),
                    ('already', 'すでに、もう'),
                    ('although', 'だけれども'),
                    ('among', 'の中で（3つ以上）'),
                    ('another', '別の、もう一つの'),
                    ('anymore', 'もはや～ない'),
                    ('appear', '現れる、～のようだ'),
                    ('arrive', '到着する'),
                    ('became', 'becomeの過去形'),
                    ('carefully', '注意深く'),
                ]
            },
            {
                'title': 'データサイエンス 英単語',
                'description': 'データサイエンス分野で使われる英単語集。統計学やデータ分析を学ぶ方におすすめです。',
                'tags': ['IT用語', '中級', '単語'],
                'cards': [
                    ('analysis', '分析'),
                    ('correlation', '相関、相関関係'),
                    ('distribution', '分布、分配'),
                    ('hypothesis', '仮説'),
                    ('inference', '推論、推測'),
                    ('outlier', '外れ値'),
                    ('regression', '回帰'),
                    ('sample', 'サンプル、標本'),
                    ('statistics', '統計学、統計'),
                    ('variable', '変数'),
                ]
            },
            {
                'title': '英語イディオム 日常編',
                'description': '日常会話でよく使われる英語のイディオム（慣用句）集。ネイティブらしい表現を学べます。',
                'tags': ['日常会話', '熟語', '中級'],
                'cards': [
                    ('break the ice', '打ち解ける、緊張をほぐす'),
                    ('piece of cake', '朝飯前、簡単なこと'),
                    ('hit the books', '勉強する'),
                    ('under the weather', '体調が悪い'),
                    ('cost an arm and a leg', '非常に高価である'),
                    ('once in a blue moon', 'めったに～ない'),
                    ('spill the beans', '秘密を漏らす'),
                    ('break a leg', '頑張って（幸運を）'),
                    ('on cloud nine', '大喜びで'),
                    ('call it a day', '今日はこれで終わりにする'),
                ]
            },
            {
                'title': '環境・SDGs関連 英単語',
                'description': '環境問題やSDGsに関する英単語集。グローバルな課題について学べます。',
                'tags': ['上級', '単語'],
                'cards': [
                    ('sustainable', '持続可能な'),
                    ('renewable', '再生可能な'),
                    ('climate change', '気候変動'),
                    ('global warming', '地球温暖化'),
                    ('carbon footprint', '二酸化炭素排出量'),
                    ('biodiversity', '生物多様性'),
                    ('ecosystem', '生態系'),
                    ('pollution', '汚染'),
                    ('conservation', '保全、保護'),
                    ('recycling', 'リサイクル、再利用'),
                ]
            },
            {
                'title': '大学受験 難関大学レベル',
                'description': '難関大学入試に対応した高度な英単語集。東大・京大レベルの語彙力を目指す方向けです。',
                'tags': ['大学受験', '上級', '単語'],
                'cards': [
                    ('accelerate', '加速する'),
                    ('contemplate', '熟考する'),
                    ('deteriorate', '悪化する'),
                    ('distinguish', '区別する、識別する'),
                    ('eliminate', '取り除く、排除する'),
                    ('fluctuate', '変動する'),
                    ('inherent', '固有の、生来の'),
                    ('manifest', '明らかにする、表す'),
                    ('predominant', '支配的な、主要な'),
                    ('substantial', '相当な、実質的な'),
                ]
            },
            {
                'title': 'ビジネス会議 英語表現',
                'description': 'ビジネス会議で使える英語表現集。プレゼンや議論で役立つフレーズを収録しています。',
                'tags': ['ビジネス英語', '中級', '文法'],
                'cards': [
                    ("Let's get started", '始めましょう'),
                    ('According to the data', 'データによれば'),
                    ('In my opinion', '私の意見では'),
                    ('Could you elaborate on that?', 'それについて詳しく説明していただけますか？'),
                    ('That makes sense', 'それは理にかなっています'),
                    ('What are your thoughts?', 'あなたのお考えは？'),
                    ("Let's move on to the next topic", '次の議題に移りましょう'),
                    ('Can we circle back to that later?', 'それは後で戻ってきましょうか？'),
                    ("I'd like to add something", '何か付け加えたいことがあります'),
                    ("Let's wrap up", 'まとめましょう'),
                ]
            },
        ]

        # 単語帳とカードを作成
        for i, wordbook_data in enumerate(wordbooks_data):
            user = sample_users[i % len(sample_users)]
            
            # ランダムなアバターと背景色を選択
            random_avatar = random.choice(AVATAR_IMAGES)
            random_bg = random.choice(BACKGROUND_COLORS)
            
            # 単語帳を作成
            wordbook = WordBook.objects.create(
                title=wordbook_data['title'],
                user=user,
                description=wordbook_data['description'],
                avatar_image=random_avatar,
                background_color=random_bg,
                is_ai_generated=True
            )
            
            self.stdout.write(f'Created wordbook: {wordbook.title} (Avatar: {random_avatar}, BG: {random_bg})')
            
            # タグを割り当て
            tags = wordbook_data.get('tags', [])
            for tag_name in tags:
                tag = Tag.objects.get(name=tag_name)
                wordbook.tags.add(tag)
            
            # 単語カードを作成
            for front, back in wordbook_data['cards']:
                WordCard.objects.create(
                    wordbook=wordbook,
                    front_text=front,
                    back_text=back
                )
            
            self.stdout.write(f'  - Added {len(wordbook_data["cards"])} cards')
            self.stdout.write(f'  - Added tags: {", ".join(tags)}')

        self.stdout.write(self.style.SUCCESS('Successfully created sample data!'))