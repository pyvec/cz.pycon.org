from django.template.response import TemplateResponse

from sponsors.models import Sponsor, SponsorsOffer


def sponsors_list(request):
    sponsors = Sponsor.objects.filter(published=True)
    return TemplateResponse(
        request, "sponsors/sponsors_list.html", {"sponsors_list": sponsors}
    )


def sponsors_offer(request):
    sponsors_offer = SponsorsOffer.objects.last()
    return TemplateResponse(
        request,
        template="sponsors/sponsors_offer.html",
        context={"sponsors_offer": sponsors_offer},
    )
