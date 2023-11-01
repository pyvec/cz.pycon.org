from pathlib import PurePath
from urllib.parse import quote

import requests
from django.contrib import admin
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils.html import format_html

from program import pretalx, pretalx_sync
from program.models import Room, Slot, Speaker, Talk, Utility, Workshop


def create_pretalx_sync() -> pretalx_sync.PretalxSync:
    client = pretalx.create_pretalx_client()
    return pretalx_sync.PretalxSync(client)


@admin.action(description="Make public")
def make_public(self, request, queryset):
    queryset.update(is_public=True)
    self.message_user(request, "Selected items have been made public.")


@admin.action(description="Make not public")
def make_not_public(self, request, queryset):
    queryset.update(is_public=False)
    self.message_user(request, "Selected items have been made not public.")


@admin.action(description="Update from pretalx")
def speaker_update_from_pretalx(modeladmin, request, queryset):
    sync = create_pretalx_sync()
    with transaction.atomic():
        sync.update_speakers(queryset)


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = [
        "full_name",
        "email",
        "is_public",
        "order",
        "photo",
        "pretalx_code",
    ]
    search_fields = ["full_name", "email", "pretalx_code"]
    list_filter = ["is_public"]
    ordering = ["order", "full_name"]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "pretalx_code",
                    "short_bio",
                    "bio",
                    "photo",
                ],
            },
        ),
        (
            "Display",
            {
                "fields": [
                    "is_public",
                    "order",
                ],
            },
        ),
        (
            "Contacts",
            {
                "fields": [
                    "twitter",
                    "github",
                    "linkedin",
                    "personal_website",
                    "email",
                ],
            },
        ),
        (
            "Speaker",
            {
                "fields": ["talks", "workshops"],
            },
        ),
    ]
    readonly_fields = [
        "full_name",
        "email",
        "bio",
        "twitter",
        "github",
        "linkedin",
        "personal_website",
        "talks",
        "workshops",
    ]
    actions = [make_public, make_not_public, speaker_update_from_pretalx]
    change_form_template = "program/admin/change_form_speaker.html"

    def get_readonly_fields(self, request, obj=None):
        ro_fields: list = super().get_readonly_fields(request, obj)
        if obj is not None and not obj.pretalx_code:
            ro_fields = ro_fields + ["pretalx_code"]
        return ro_fields

    def save_model(self, request, obj: Speaker, form, change: bool) -> None:
        obj.save()

        if not change and obj.pretalx_code:
            sync = create_pretalx_sync()
            sync.update_speakers([obj])


@admin.action(description="Update from pretalx")
def talk_update_from_pretalx(modeladmin, request, queryset):
    sync = create_pretalx_sync()
    with transaction.atomic():
        sync.update_talks(queryset)


@admin.register(Talk)
class TalkAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "speakers",
        "track",
        "language",
        "order",
        "is_keynote",
        "is_public",
        "is_backup",
        "pretalx_code",
    ]
    list_filter = ["is_keynote", "track", "type", "language", "is_public", "is_backup"]
    search_fields = ["title", "abstract", "talk_speakers__full_name", "pretalx_code"]
    ordering = ["is_backup", "-is_keynote", "track", "order", "title"]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "pretalx_code",
                    "og_image",
                ],
            },
        ),
        (
            "Display",
            {
                "fields": [
                    ("is_public", "is_backup"),
                    "order",
                ],
            },
        ),
        (
            "Slides and Video",
            {
                "fields": [
                    "video_url",
                    "video_image_html",
                    "slides_file",
                    "slides_description",
                ],
            },
        ),
        (
            "Talk info (edit in pretalx)",
            {
                "fields": [
                    "title",
                    "track",
                    "private_note",
                    "type",
                    "speakers",
                    "language",
                    "minimum_python_knowledge",
                    "minimum_topic_knowledge",
                    "abstract",
                ],
            },
        ),
    ]
    readonly_fields = [
        "title",
        "speakers",
        "is_keynote",
        "abstract",
        "track",
        "private_note",
        "language",
        "minimum_python_knowledge",
        "minimum_topic_knowledge",
        "type",
        "video_image_html",
    ]
    actions = [make_public, make_not_public, talk_update_from_pretalx]
    change_form_template = "program/admin/change_form_session.html"

    @admin.display(description="Video Image")
    def video_image_html(self, obj: Talk):
        if not obj.video_image:
            return "(no image)"

        html = (
            '<a href="{image_url}" style="display: inline-block">'
            '<img src="{image_url}" height="180"/><br>'
            '<span style="display: inline-block; margin-top: 1ex;">{image_name}</span>'
            "</a>"
        )

        return format_html(
            html,
            image_url=obj.video_image.url,
            image_name=obj.video_image.name,
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related("talk_speakers")
        return qs

    @admin.display(description="Speakers", empty_value="not set")
    def speakers(self, talk: Talk) -> str:
        return ", ".join(speaker.full_name for speaker in talk.talk_speakers.all())

    def get_readonly_fields(self, request, obj=None):
        ro_fields: list = super().get_readonly_fields(request, obj)
        if obj is not None and not obj.pretalx_code:
            ro_fields = ro_fields + ["pretalx_code"]
        return ro_fields

    def save_model(self, request, obj: Talk, form, change: bool) -> None:
        if change:
            self._update_video_image(obj)

        obj.save()

        if not change and obj.pretalx_code:
            sync = create_pretalx_sync()
            sync.update_talks([obj])

    def _update_video_image(self, talk: Talk):
        video_id = talk.video_id
        if not video_id:
            # Delete the existing image, if any.
            if talk.video_image:
                talk.video_image.delete(save=False)
            return

        # Get the video ID of the current image:
        # the image is always named <video_id>.jpg
        image_video_id: str | None = None
        if talk.video_image:
            image_path = PurePath(talk.video_image.name)
            image_video_id = image_path.stem

        # Check if the video ID has changed and download a new image when necessary.
        if video_id != image_video_id:
            image_data = self._download_youtube_video_image(video_id)
            talk.video_image.save(
                name=image_data.name,
                content=image_data,
                save=False,
            )

    def _download_youtube_video_image(self, video_id: str) -> ContentFile:
        image_url = self._format_youtube_video_image_url(video_id)

        with requests.get(image_url, timeout=30) as image_response:
            image_response.raise_for_status()
            return ContentFile(
                content=image_response.content,
                name=f"{video_id}.jpg",
            )

    def _format_youtube_video_image_url(self, video_id):
        return f"https://img.youtube.com/vi/{quote(video_id)}/maxresdefault.jpg"


@admin.action(description="Update from pretalx")
def workshop_update_from_pretalx(modeladmin, request, queryset):
    sync = create_pretalx_sync()
    with transaction.atomic():
        sync.update_workshops(queryset)


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "speakers",
        "track",
        "language",
        "order",
        "is_public",
        "is_backup",
        "pretalx_code",
    ]
    list_filter = ["type", "track", "type", "language", "is_public", "is_backup"]
    search_fields = [
        "title",
        "abstract",
        "workshop_speakers__full_name",
        "pretalx_code",
    ]
    ordering = ["is_backup", "track", "order", "title"]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "pretalx_code",
                    "og_image",
                    "registration",
                    "length",
                    "is_sold_out",
                ],
            },
        ),
        (
            "Display",
            {
                "fields": [
                    ("is_public", "is_backup"),
                    "order",
                ],
            },
        ),
        (
            "Workshop info (edit in pretalx)",
            {
                "fields": [
                    "title",
                    "track",
                    "attendee_limit",
                    "private_note",
                    "type",
                    "speakers",
                    "language",
                    "minimum_python_knowledge",
                    "minimum_topic_knowledge",
                    "requirements",
                    "abstract",
                ],
            },
        ),
    ]
    readonly_fields = [
        "title",
        "speakers",
        "abstract",
        "requirements",
        "track",
        "private_note",
        "language",
        "minimum_python_knowledge",
        "minimum_topic_knowledge",
        # "type",
        "attendee_limit",
    ]
    actions = [make_public, make_not_public, workshop_update_from_pretalx]
    change_form_template = "program/admin/change_form_session.html"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related("workshop_speakers")
        return qs

    @admin.display(description="Speakers", empty_value="not set")
    def speakers(self, workshop: Workshop) -> str:
        return ", ".join(
            speaker.full_name for speaker in workshop.workshop_speakers.all()
        )

    def get_readonly_fields(self, request, obj=None):
        ro_fields: list = super().get_readonly_fields(request, obj)
        if obj is not None and not obj.pretalx_code:
            ro_fields = ro_fields + ["pretalx_code"]
        return ro_fields

    def save_model(self, request, obj: Workshop, form, change: bool) -> None:
        obj.save()

        if not change and obj.pretalx_code:
            sync = create_pretalx_sync()
            sync.update_workshops([obj])


@admin.register(Utility)
class UtilityAdmin(admin.ModelAdmin):
    empty_value_display = "not set"
    list_display = [
        "title",
        "short_description",
        "url",
        "is_streamed",
    ]
    list_editable = [
        "is_streamed",
    ]
    prepopulated_fields = {
        "slug": ["title"],
    }

    @admin.display(description="Description", empty_value="not set")
    def short_description(self, obj: Utility) -> str | None:
        """Shorten the description for admin inline.

        If there is no description, return None, so the "empty_value" fires.
        """
        return obj.description[:180] + "..." if obj.description else None


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = [
        "label",
        "order",
        "slug",
    ]
    list_editable = [
        "order",
    ]
    fields = [
        "label",
        "order",
        "slug",
    ]
    prepopulated_fields = {
        "slug": ["label"],
    }


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = [
        "event",
        "start",
        "end",
        "room",
    ]
    list_filter = [
        "room",
    ]
    list_editable = [
        "room",
        "start",
        "end",
    ]
    fieldsets = [
        (
            "Event",
            {
                "description": "Select only one of the following.",
                "fields": [
                    "talk",
                    "workshop",
                    "utility",
                ],
            },
        ),
        (
            "Times",
            {
                "fields": [
                    ("start", "end"),
                ],
            },
        ),
        (
            None,
            {
                "fields": [
                    "room",
                ],
            },
        ),
    ]
    date_hierarchy = "start"
