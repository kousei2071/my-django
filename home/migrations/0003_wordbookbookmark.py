from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_wordbooklike'),
    ]

    operations = [
        migrations.CreateModel(
            name='WordBookBookmark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='bookmarked_wordbooks', to=settings.AUTH_USER_MODEL)),
                ('wordbook', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='bookmarks', to='home.wordbook')),
            ],
            options={
                'unique_together': {('user', 'wordbook')},
            },
        ),
        migrations.AddIndex(
            model_name='wordbookbookmark',
            index=models.Index(fields=['user', 'wordbook'], name='home_wordbo_user_id_1c80c6_idx'),
        ),
    ]
