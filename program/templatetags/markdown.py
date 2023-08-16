import mistune
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdown")
def render_markdown(markdown_source: str) -> str:
    markdown = mistune.create_markdown(plugins=["strikethrough", "table", "url"])
    result = markdown(markdown_source)
    return mark_safe(result)
