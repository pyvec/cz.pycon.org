import mistune
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


class CustomRenderer(mistune.HTMLRenderer):
    def heading(self, text: str, level: int, **attrs) -> str:
        level += 1  # start headings at h2
        tag = 'h' + str(level)
        html = '<' + tag
        _id = attrs.get('id')
        if _id:
            html += ' id="' + _id + '"'
        return html + '>' + text + '</' + tag + '>\n'


@register.filter(name="markdown")
def render_markdown(markdown_source: str) -> str:
    markdown = mistune.create_markdown(
        renderer=CustomRenderer(),
        plugins=["strikethrough", "table", "url"]
    )
    result = markdown(markdown_source)
    return mark_safe(result)
