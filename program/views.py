import datetime
import re

from django.http import HttpRequest, Http404
from django.template.loader import render_to_string
from django.template.response import TemplateResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from program.models import Talk, Workshop, Slot


# Note: conference days are currently hardcoded.
# We could build the list directly from the database to make the code more
# re-usable for the next year, but right now it seems like an overkill.
CONFERENCE_DAYS = {
    "friday": datetime.date(2023, 9, 15),
    "saturday": datetime.date(2023, 9, 16),
    "sunday": datetime.date(2023, 9, 17),
}


def session_detail(request, type, session_id: int):
    model_map = dict(talk=Talk, panel=Talk, workshop=Workshop, sprint=Workshop)
    session = get_object_or_404(model_map.get(type), id=session_id, is_public=True, is_backup=False)

    # session_slot = Slot.objects.filter(
    #     content_type__app_label='program',
    #     content_type__model=dict(talk='talk', workshop='workshop', sprint='workshop').get(type),
    #     object_id=session_id,
    # ).first()

    session_previous = model_map.get(type).objects.filter(
        is_public=True, is_backup=False, order__lt=session.order).order_by('order').last()

    if not session_previous:  # at the first session provide the last one as previous
        session_previous = model_map.get(type).objects.filter(
            is_public=True, is_backup=False).order_by('order').last()

    session_next = model_map.get(type).objects.filter(
        is_public=True, is_backup=False, order__gt=session.order).order_by('order').first()

    if not session_next:  # at the last session provide the first one as next
        session_next = model_map.get(type).objects.filter(
            is_public=True, is_backup=False).order_by('order').first()

    # slots_remaining_in_day = Slot.objects.filter(
    #     content_type__app_label='program',
    #     content_type__model__in=['talk', 'workshop', 'utility'],
    #     start__gte=session_slot.start,
    #     start__day=session_slot.start.day,
    # ).prefetch_related(
    #     'content_object',
    # ).order_by('start', 'room')

    # remove redundant slots
    # note: this expects that sessions and utilities do not mix at the same time
    # previous_slot = None
    # rows_having_session = 0
    # slots = []

    # for slot in slots_remaining_in_day:
    #     if previous_slot and previous_slot.start != slot.start:  # when new row starts
    #         # did previous row have a session?
    #         if str(previous_slot.content_type) in ['talk', 'workshop']:
    #             rows_having_session += 1
    #             # only current and one future row with sessions is needed
    #             if rows_having_session >= 2:
    #                 break
    #     slots.append(slot)
    #     previous_slot = slot

    return TemplateResponse(
        request,
        template='program/{}_detail.html'.format(type),
        context={
            'session': session,
            'other_sessions': {
                'previous': session_previous,
                'next': session_next,
            },
            # 'session_slot': session_slot,
            # 'slots': slots,
        }
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


def schedule_redirect(request) -> HttpResponse:
    # Gets time in the local timezone (Europe/Prague, as set in settings.py).
    today = timezone.localdate()
    selected_day = None
    for conference_day, date_value in CONFERENCE_DAYS.items():
        # Redirect to first day by default
        if selected_day is None:
            selected_day = conference_day
        if date_value == today:
            selected_day = conference_day
            break

    response = redirect(
        to="program:schedule_day",
        conference_day=selected_day,
        permanent=False,
    )
    # Add a caching header to make sure it is not stored in any cache.
    response.headers['Cache-Control'] = 'no-store'
    return response


def schedule_day(request: HttpRequest, conference_day: str) -> HttpResponse:
    try:
        schedule_date = CONFERENCE_DAYS[conference_day]
    except KeyError:
        raise Http404()

    slots = Slot.objects.filter(start__date=schedule_date)
    return TemplateResponse(
        request,
        template="program/schedule_day.html",
        context={
            "schedule_date": schedule_date,
            "slots": slots,
        },
    )


def debug_og_image_for_talk(request, session_id: int) -> HttpResponse:
    """
    DEBUG view: preview OG image template for a talk.
    """
    talk = get_object_or_404(Talk, pk=session_id)
    return _render_og_template(
        request,
        template="program/og_images/talk.html",
        context={"session": talk},
    )


def debug_og_image_for_workshop(request, session_id: int) -> HttpResponse:
    """
    DEBUG view: preview OG image template for a workshop.
    """
    workshop = get_object_or_404(Workshop, pk=session_id)
    return _render_og_template(
        request,
        template="program/og_images/workshop.html",
        context={"session": workshop},
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
