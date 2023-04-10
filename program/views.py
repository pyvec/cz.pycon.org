from django.template.response import TemplateResponse

from program.models import Speaker, Talk, Workshop


def preview(request):
    speakers = Speaker.objects.prefetch_related("talks", "workshops").order_by(
        "full_name"
    )

    return TemplateResponse(
        request, template="program/preview.html", context={"speakers": speakers}
    )


def talks_list(request):
    talks = Talk.objects.filter(is_backup=False)
    public_talks = talks.filter(is_public=True).order_by("order")
    more_to_come = talks.filter(is_public=False).exists()

    return TemplateResponse(
        request,
        template="program/talks_list.html",
        context={"sessions": public_talks, "more_to_come": more_to_come},
    )


def workshops_list(request):
    workshops = Workshop.objects.filter(is_backup=False)
    public_workshops = workshops.filter(is_public=True).order_by("order")
    more_to_come = workshops.filter(is_public=False).exists()

    return TemplateResponse(
        request,
        template="program/workshops_list.html",
        context={"sessions": public_workshops, "more_to_come": more_to_come},
    )
