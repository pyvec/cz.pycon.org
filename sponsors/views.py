from django.template.response import TemplateResponse

from sponsors.models import Sponsor


def sponsors_list(request):
    sponsors = Sponsor.objects.filter(published=True)
    return TemplateResponse(
        request, "sponsors/sponsors_list.html", {"sponsors_list": sponsors}
    )
