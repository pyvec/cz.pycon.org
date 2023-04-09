import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdown")
def markdown(text):
    return mark_safe(md.markdown(text, safe_mode="escape"))
