from django.db.models import Count
from .models import Tag


def tags_processor(request):
    """全ページで人気タグと選択中のタグを利用可能にする"""
    # 人気タグTOP10を取得
    popular_tags = Tag.objects.annotate(
        usage_count=Count('wordbooks')
    ).filter(usage_count__gt=0).order_by('-usage_count', 'name')[:10]
    
    # 選択中のタグ
    tag_name = request.GET.get('tag')
    selected_tag_names = []
    if tag_name:
        selected_tag_names = [tag_name]
    
    return {
        'popular_tags': popular_tags,
        'selected_tag_names': selected_tag_names,
    }
