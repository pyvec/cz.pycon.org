from django.template.response import TemplateResponse

from announcements.models import Announcement
from sponsors.models import Sponsor


def index(request):
    return TemplateResponse(
        request,
        template="intermissions/index.html",
        context={
            # if 'interval' is not passed in GET request,
            # then it's called every 10 seconds
            "interval": int(request.GET.get("interval", 10))
            * 1000,
        },
    )


def sponsors(request, level):
    sponsors = Sponsor.objects.filter(published=True, level=level)

    first_sponsor = sponsors.first()
    # get readable display name for the passed level (integer)
    level_name = first_sponsor.get_level_display() if first_sponsor else None
    level_slug = level if first_sponsor else None

    return TemplateResponse(
        request,
        template="intermissions/sponsors.html",
        context={
            "sponsors": sponsors,
            "level_name": level_name,
            "level_slug": level_slug,
        },
    )


def announcements(request):
    return TemplateResponse(
        request,
        template="intermissions/announcements.html",
        context={
            "announcements": Announcement.objects.filter(is_public=True)[:7],
        },
    )


def slido(request):
    return TemplateResponse(
        request,
        template="intermissions/slido.html",
    )
