import re

from django.template.loader import render_to_string
from django.template.response import TemplateResponse, HttpResponse
from django.shortcuts import get_object_or_404

from program.models import Talk, Workshop


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


def debug_og_image_for_talk(request, session_id: int) -> HttpResponse:
    """
    DEBUG view: preview OG image template for a talk.
    """
    talk = get_object_or_404(Talk, pk=session_id)
    return _render_og_template(
        request,
        template="program/og_images/talk.html",
        context={"talk": talk},
    )


def debug_og_image_for_workshop(request, session_id: int) -> HttpResponse:
    """
    DEBUG view: preview OG image template for a workshop.
    """
    workshop = get_object_or_404(Workshop, pk=session_id)
    return _render_og_template(
        request,
        template="program/og_images/workshop.html",
        context={"workshop": workshop},
    )


def _render_og_template(request, template: str, context: dict) -> HttpResponse:
    rendered_html = render_to_string(template, context)
    rendered_html = _make_absolute_urls(
        rendered_html,
        [
            "media/",
            "static/",
        ],
    )

    return HttpResponse(
        status=200,
        content=rendered_html,
        content_type="text/html; charset=utf-8",
    )


def _make_absolute_urls(html_source: str, paths: list[str]) -> str:
    path_expr = "|".join(re.escape(path) for path in paths)
    return re.sub(rf"(?<!/)(?P<path>{path_expr})", r"/\g<path>", html_source)
