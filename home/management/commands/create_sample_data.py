from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from home.models import WordBook, WordCard

class Command(BaseCommand):
    help = 'Create sample wordbooks and wordcards'

    def handle(self, *args, **options):
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

        # サンプル単語帳データ
        wordbooks_data = [
            {
                'title': 'TOEIC必須単語 600点レベル',
                'description': 'TOEIC 600点を目指すための基本的な英単語集です。ビジネスシーンでよく使われる単語を中心に収録しています。',
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
        ]

        # 単語帳とカードを作成
        for i, wordbook_data in enumerate(wordbooks_data):
            user = sample_users[i % len(sample_users)]
            
            # 既に同じタイトルの単語帳が存在するかチェック
            wordbook, created = WordBook.objects.get_or_create(
                title=wordbook_data['title'],
                user=user,
                defaults={'description': wordbook_data['description']}
            )
            
            if created:
                self.stdout.write(f'Created wordbook: {wordbook.title}')
                
                # 単語カードを作成
                for front, back in wordbook_data['cards']:
                    WordCard.objects.create(
                        wordbook=wordbook,
                        front_text=front,
                        back_text=back
                    )
                
                self.stdout.write(f'  - Added {len(wordbook_data["cards"])} cards')
            else:
                self.stdout.write(f'Wordbook already exists: {wordbook.title}')

        self.stdout.write(self.style.SUCCESS('Successfully created sample data!'))