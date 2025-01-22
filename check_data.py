#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from home.models import wordBookLike, WordBookBookmark

print(f'Total users: {User.objects.count()}')
print(f'Total likes: {wordBookLike.objects.count()}')
print(f'Total bookmarks: {WordBookBookmark.objects.count()}')

print('\nLikes:')
for like in wordBookLike.objects.all()[:10]:
    print(f'  User: {like.user.username} (ID: {like.user.id})')
    print(f'  Wordbook: {like.wordbook.title} (ID: {like.wordbook.id})')
    print(f'  Created: {like.created_at}')
    print()

print('\nBookmarks:')
for bm in WordBookBookmark.objects.all()[:10]:
    print(f'  User: {bm.user.username} (ID: {bm.user.id})')
    print(f'  Wordbook: {bm.wordbook.title} (ID: {bm.wordbook.id})')
    print(f'  Created: {bm.created_at}')
    print()
