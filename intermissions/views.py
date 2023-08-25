from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django.db.models import Count

from announcements.models import Announcement
from sponsors.models import Sponsor, Level


def index(request):
    levels  = {
        l.slug for l in
        Level.objects.annotate(sponsor_count=Count('sponsor')).filter(sponsor_count__gt=0)
    }
    
    return TemplateResponse(
        request,
        template="intermissions/index.html",
        context={
            # if 'interval' is not passed in GET request,
            # then it's called every 10 seconds
            "interval": int(request.GET.get("interval", 10)) * 1000,
            "levels": levels,
        },
    )


def sponsors(request, level):
    level = get_object_or_404(Level, slug=level)
    sponsors = Sponsor.objects.filter(published=True, level=level)

    first_sponsor = sponsors.first()
    # get readable display name for the passed level (integer)
    
    return TemplateResponse(
        request,
        template="intermissions/sponsors.html",
        context={
            "sponsors": sponsors,
            "level": level
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
