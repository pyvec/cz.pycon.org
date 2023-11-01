import re

from django import template

register = template.Library()


@register.filter(name="regexextract")
def regexextract(value, regex_pattern):
    try:
        match = re.search(regex_pattern, value)
        if match:
            return match.group(1) if match.groups() else match.group(0)
        else:
            return ""
    except re.error:
        return ""
