from django.template.response import TemplateResponse

from team.models import Organizer, TeamPage


def team_list(request):
    organizers = Organizer.objects.filter(published=True)
    team_page = TeamPage.objects.last()

    return TemplateResponse(
        request,
        template="team/organizers_list.html",
        context={"organizers": organizers, "team_page": team_page},
    )
