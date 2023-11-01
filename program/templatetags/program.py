import datetime
import math
import re

from django import template
from django.utils.translation import ngettext

register = template.Library()


@register.filter(name="session_length")
def session_length(value: datetime.timedelta) -> str:
    total_minutes = round(value.total_seconds() / 60)
    hours = math.floor(total_minutes / 60)
    minutes = total_minutes % 60

    parts = []
    if hours > 0:
        parts.append(
            ngettext("%(num)d hour", "%(num)d hours", hours) % {"num": hours},
        )
    if minutes > 0:
        parts.append(
            ngettext("%(num)d minute", "%(num)d minutes", minutes) % {"num": minutes}
        )

    return " ".join(parts)


@register.filter(name="auto_nbsp")
def auto_nbsp(value: str) -> str:
    return re.sub(
        r"\b(?P<word>the|a|of|to|on|\w) ",
        "\g<word> ",
        value,
        flags=re.RegexFlag.IGNORECASE,
    )
