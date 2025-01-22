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
                    ('article', '記事、品物'),
                    ('atmosphere', '雰囲気、大気'),
                ]
            },
            {
                'title': 'ビジネス英語 メール編',
                'description': 'ビジネスメールでよく使う表現を集めました。実践的なフレーズばかりです。',
                'cards': [
                    ('regarding', '～に関して'),
                    ('attached', '添付された'),
                    ('following up', 'フォローアップ、追跡'),
                    ('inquiry', '問い合わせ、質問'),
                    ('confirmation', '確認'),
                    ('apologize', '謝罪する'),
                    ('appreciate', '感謝する'),
                    ('deadline', '締め切り'),
                    ('reschedule', '予定を変更する'),
                    ('clarification', '明確化、説明'),
                ]
            },
            {
                'title': '旅行英会話 必須フレーズ',
                'description': '海外旅行で役立つ英会話フレーズ。空港、ホテル、レストランで使えます。',
                'cards': [
                    ('Where is the gate?', 'ゲートはどこですか？'),
                    ("I'd like to check in", 'チェックインしたいのですが'),
                    ('Do you have a vacancy?', '空室はありますか？'),
                    ('Can I have the menu?', 'メニューをいただけますか？'),
                    ("I'd like to order", '注文したいのですが'),
                    ('How much is this?', 'これはいくらですか？'),
                    ('Where is the restroom?', 'トイレはどこですか？'),
                    ('Can you help me?', '助けていただけますか？'),
                    ('I lost my passport', 'パスポートをなくしました'),
                    ('Call a taxi, please', 'タクシーを呼んでください'),
                ]
            },
            {
                'title': '医療英単語 基礎編',
                'description': '医療・健康に関する基本的な英単語。病院や薬局で役立ちます。',
                'cards': [
                    ('symptom', '症状'),
                    ('diagnosis', '診断'),
                    ('prescription', '処方箋'),
                    ('medicine', '薬、医学'),
                    ('treatment', '治療'),
                    ('examination', '検査、診察'),
                    ('hospital', '病院'),
                    ('patient', '患者'),
                    ('doctor', '医者'),
                    ('nurse', '看護師'),
                ]
            },
            {
                'title': '食べ物・料理の英単語',
                'description': '食材や料理に関する英単語集。レシピを読んだり、レストランで注文する時に便利です。',
                'cards': [
                    ('ingredient', '材料、成分'),
                    ('recipe', 'レシピ、調理法'),
                    ('boil', '煮る、沸騰させる'),
                    ('fry', '炒める、揚げる'),
                    ('bake', '焼く（オーブンで）'),
                    ('season', '味付けする'),
                    ('vegetarian', 'ベジタリアン、菜食主義者'),
                    ('appetizer', '前菜'),
                    ('dessert', 'デザート'),
                    ('beverage', '飲み物'),
                ]
            },
            {
                'title': 'TOEFL iBT 頻出単語',
                'description': 'TOEFL iBTテストでよく出る学術的な英単語を厳選しました。',
                'cards': [
                    ('abundant', '豊富な、たくさんの'),
                    ('analyze', '分析する'),
                    ('assume', '仮定する、想定する'),
                    ('authority', '権威、当局'),
                    ('available', '利用可能な'),
                    ('beneficial', '有益な'),
                    ('category', 'カテゴリー、分類'),
                    ('consist', '成り立つ、構成される'),
                    ('crucial', '重要な、決定的な'),
                    ('demonstrate', '実証する、示す'),
                ]
            },
            {
                'title': '天気・自然の英単語',
                'description': '天気予報や自然に関する英単語。日常会話でもよく使います。',
                'cards': [
                    ('weather', '天気'),
                    ('forecast', '予報、予測'),
                    ('temperature', '気温、温度'),
                    ('humidity', '湿度'),
                    ('precipitation', '降水量'),
                    ('thunderstorm', '雷雨'),
                    ('drought', '干ばつ'),
                    ('climate', '気候'),
                    ('season', '季節'),
                    ('atmosphere', '大気、雰囲気'),
                ]
            },
            {
                'title': 'スポーツ英単語 初級',
                'description': 'スポーツに関する基本的な英単語とフレーズを集めました。',
                'cards': [
                    ('athlete', '運動選手'),
                    ('competition', '競技、競争'),
                    ('tournament', 'トーナメント、大会'),
                    ('champion', 'チャンピオン、優勝者'),
                    ('score', '得点、スコア'),
                    ('referee', '審判'),
                    ('training', 'トレーニング、訓練'),
                    ('victory', '勝利'),
                    ('defeat', '敗北'),
                    ('team', 'チーム'),
                ]
            },
            {
                'title': '感情を表す英単語',
                'description': '様々な感情や気持ちを表現する英単語集。会話がより豊かになります。',
                'cards': [
                    ('happy', '幸せな、嬉しい'),
                    ('excited', '興奮した、ワクワクした'),
                    ('nervous', '緊張した、不安な'),
                    ('disappointed', 'がっかりした'),
                    ('frustrated', 'イライラした'),
                    ('relieved', '安心した、ほっとした'),
                    ('confused', '混乱した、困惑した'),
                    ('grateful', '感謝している'),
                    ('anxious', '不安な、心配な'),
                    ('proud', '誇らしい、自慢の'),
                ]
            },
            {
                'title': '音楽用語の英単語',
                'description': '音楽に関する基本的な英単語。楽器や音楽理論の用語を学べます。',
                'cards': [
                    ('instrument', '楽器'),
                    ('melody', 'メロディー、旋律'),
                    ('rhythm', 'リズム、拍子'),
                    ('harmony', 'ハーモニー、調和'),
                    ('tempo', 'テンポ、速さ'),
                    ('composer', '作曲家'),
                    ('conductor', '指揮者'),
                    ('performance', '演奏、公演'),
                    ('orchestra', 'オーケストラ'),
                    ('choir', '合唱団'),
                ]
            },
            {
                'title': '英単語 難易度ハイレベル編',
                'description': '英検1級やTOEFL/IELTS高得点を目指す方のための、難易度の高い英単語集です。',
                'cards': [
                    ('ubiquitous', '至る所にある、遍在する'),
                    ('meticulous', '細心の注意を払う、几帳面な'),
                    ('ephemeral', 'つかの間の、儚い'),
                    ('quintessential', '典型的な、本質的な'),
                    ('obfuscate', '分かりにくくする、曖昧にする'),
                    ('perfunctory', 'おざなりの、いい加減な'),
                    ('idiosyncratic', '特有の、風変わりな'),
                    ('magnanimous', '寛大な、度量の大きい'),
                    ('equanimity', '平静、落ち着き'),
                    ('incontrovertible', '議論の余地のない、明白な'),
                ]
            }
            ,
            {
                'title': '英検3級 重要単語',
                'description': '英検3級合格のために覚えておきたい基本単語を集めました。中学卒業レベルの語彙力向上に最適です。',
                'cards': [
                    ('answer', '答える、答え'),
                    ('question', '質問、問題'),
                    ('travel', '旅行する'),
                    ('family', '家族'),
                    ('future', '未来、将来'),
                    ('important', '重要な'),
                    ('different', '異なる、違う'),
                    ('sometimes', 'ときどき'),
                    ('together', '一緒に'),
                    ('remember', '覚えている、思い出す'),
                ]
            }
        
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