from django.template.response import TemplateResponse

from .models import Organizer


def team_list(request):
    organizers = Organizer.objects.filter(published=True).order_by("?")

    return TemplateResponse(
        request,
        template="team/organizers_list.html",
        context={"organizers": organizers},
    )
