from django import template
from django.templatetags.static import static
from django.contrib.staticfiles import finders
import os

register = template.Library()


@register.simple_tag
def static_version(path):
    """Return static URL with a version query param based on file mtime.

    Usage in template:
        {% static_version 'home/css/style.css' %}
    """
    url = static(path)
    try:
        abs_path = finders.find(path)
        if abs_path and os.path.exists(abs_path):
            mtime = int(os.path.getmtime(abs_path))
            return f"{url}?v={mtime}"
    except Exception:
        # If any error, fall back to plain static url
        pass
    return url
