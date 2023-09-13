import datetime
import re
from typing import Iterable, NamedTuple
from urllib.parse import quote

from django.http import HttpRequest, HttpResponse, Http404
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone

from announcements.models import Announcement
from sponsors.models import Sponsor, Level
from program.models import Slot
from program.views import CONFERENCE_DAYS


MAX_TALK_PAGE = 2


def index(request):
    levels = {
        l.slug
        for l in Level.objects.annotate(sponsor_count=Count("sponsor")).filter(
            sponsor_count__gt=0
        )
    }

    time_param = ""
    if simulated_time := request.GET.get("time", None):
        time_param = f"?time={quote(simulated_time)}"

    return TemplateResponse(
        request,
        template="intermissions/index.html",
        context={
            # if 'interval' is not passed in GET request,
            # then it's called every 10 seconds
            "interval": int(request.GET.get("interval", 10)) * 1000,
            "levels": levels,
            "time_param": time_param,
        },
    )


def sponsors(request, level: str):
    """
    This view renders a list of sponsors for the given level.

    The level argument can be given as:

    * A level slug, e.g., ``silver``.
    * A level slug followed by a slice, e.g., ``silver[:6]`` - you can use the
      Python slicing syntax, however, the step parameter is not supported.
    * List with any of the above separated by comma, e.g. ``afterparty[:1],coffee``.
    """
    level_list = level.split(',')
    sponsor_lists: list['SponsorList'] = []

    for level in level_list:
        level_slug, sponsor_slice = _parse_level_slice(level.strip())

        level = get_object_or_404(Level, slug=level_slug)
        sponsors = Sponsor.objects.filter(published=True, level=level)

        if sponsor_slice is not None:
            sponsors = sponsors[sponsor_slice]

        # Skip empty levels
        if len(sponsors) == 0:
            continue
        sponsor_lists.append(SponsorList(level, sponsors))

    return TemplateResponse(
        request,
        template="intermissions/sponsors.html",
        context={
            "sponsor_lists": sponsor_lists,
        },
    )


class SponsorList(NamedTuple):
    level: Level
    sponsors: Iterable[Sponsor]


def _parse_level_slice(level_spec: str) -> tuple[str, slice | None]:
    def parse_slice_index(idx: str) -> int | None:
        if idx == '':
            return None
        return int(idx)

    slice_match = re.fullmatch(
        r"(?P<level>\w+)\[(?P<start>\d*)(:(?P<end>\d*))?]",
        level_spec,
    )
    if not slice_match:
        return level_spec, None

    level = slice_match["level"]
    start_index = parse_slice_index(slice_match["start"])
    if slice_match["end"] is not None:
        result_slice = slice(start_index, parse_slice_index(slice_match["end"]))
    else:
        result_slice = slice(start_index)
    return level, result_slice


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


def next_talk(request: HttpRequest, page: int) -> HttpResponse:
    # Only 2 pages is supported in this variant.
    if page < 1 or page > MAX_TALK_PAGE:
        raise Http404()

    # You can simulate the time using the time GET parameter.
    simulated_time = request.GET.get("time", None)

    default_tz = timezone.get_default_timezone()
    if simulated_time:
        current_time = datetime.datetime.fromisoformat(simulated_time)
        current_time = current_time.replace(tzinfo=default_tz)

    else:
        current_time = timezone.now()
        # Hey, you might try this before the conference starts!
        # Simulate the first day of the conference.
        conference_start_date = min(CONFERENCE_DAYS.values())
        conference_start = datetime.datetime.combine(
            date=conference_start_date,
            time=datetime.time(9, 0),
            tzinfo=default_tz,
        )
        if current_time < conference_start:
            current_time = conference_start

    upcoming_slots = _get_upcoming_slots(current_time)
    upcoming_slots, streamed = _detect_streamed_slots(upcoming_slots)
    slide_slots = _get_slots_for_page(upcoming_slots, page)

    return TemplateResponse(
        request,
        "intermissions/next_talk.html",
        context={
            "slots": slide_slots,
            "streamed": streamed,
        },
    )


def _get_upcoming_slots(current_time: datetime.datetime) -> list[Slot]:
    # Add 5 minutes start tolerance - just in case something goes wrong on-site
    # and the talk starts a bit late.
    start_time = current_time - datetime.timedelta(minutes=5)
    # On Saturday, some rooms are empty until afternoon - don't advertise them early.
    start_time_max = current_time + datetime.timedelta(hours=1, minutes=15)
    upcoming_slots = (
        Slot.objects.filter(
            start__gte=start_time,
            start__lte=start_time_max,
        )
        .filter(
            # Lunch is inevitable, no need to advertise it.
            # Show only talks or streamed utilities.
            Q(talk_id__isnull=False)
            | Q(utility_id__isnull=False, utility__is_streamed=True)
        )
        .distinct(
            # Generates a DISTINCT ON() clause, which returns only the first row
            # with the given value - will return only the next upcoming slot
            # for each room.
            "room_id"
        )
        .select_related(
            "room",
            "talk",
            "utility",
        )
        .order_by(
            # Column used in DISTINCT ON must be the first column in ORDER BY
            "room_id",
            "start",
        )
    )

    # Sort the slots by room order in Python (sorting 4 rows should be fast enough).
    # For more rooms, sorting in database using a subquery might be more efficient.
    result = list(upcoming_slots)
    result.sort(key=lambda slot: slot.room.order)
    return result


def _detect_streamed_slots(upcoming_slots: list[Slot]) -> tuple[list[Slot], bool]:
    streamed = False
    result = []
    for slot in upcoming_slots:
        if result and slot.is_same_for_different_room(result[-1]):
            streamed = True
            continue

        result.append(slot)
        if slot.utility is not None and slot.utility.is_streamed:
            streamed = True

    return result, streamed


def _get_slots_for_page(slots: list[Slot], page) -> list[Slot]:
    # If there is only 1 slot, show it on both pages.
    if len(slots) == 1:
        return slots

    # If there are 2 slots, show each one on its own page.
    if len(slots) == 2:
        return slots[page - 1 : page]

    # In case of 3 slots, put 1 slot on the first page, 2 on the second page.
    # This expression might be too complex for this simple case,
    # but it allows adding more pages in the future.
    start_index = max(0, len(slots) - (MAX_TALK_PAGE - page + 1) * 2)
    end_index = len(slots) - (MAX_TALK_PAGE - page) * 2
    return slots[start_index:end_index]
