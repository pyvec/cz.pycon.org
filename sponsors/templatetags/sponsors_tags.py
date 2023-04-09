from django import template

from sponsors.models import Sponsor

register = template.Library()


@register.simple_tag()
def get_sponsors():
    return Sponsor.objects.filter(published=True)
