from django.contrib import admin
from django.db import transaction

from program.models import Speaker, Talk, Workshop
from program import pretalx
from program import pretalx_sync


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
        "display_position",
        "photo",
        "pretalx_code",
    ]
    search_fields = ["full_name", "email", "pretalx_code"]
    list_filter = ["is_public"]
    ordering = ["full_name"]
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
                    "display_position",
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
        "is_keynote",
        "track",
        "language",
        "order",
        "is_public",
        "is_backup",
        "pretalx_code",
    ]
    list_filter = ["is_keynote", "track", "language", "is_public", "is_backup"]
    search_fields = ["title", "abstract", "talk_speakers__full_name", "pretalx_code"]
    ordering = ["is_backup", "-is_keynote", "track", "order", "title"]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "pretalx_code",
                    "og_image",
                    "video_id",
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
    ]
    actions = [make_public, make_not_public, talk_update_from_pretalx]

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
        obj.save()

        if not change and obj.pretalx_code:
            sync = create_pretalx_sync()
            sync.update_talks([obj])


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
    list_filter = ["type", "track", "language", "is_public", "is_backup"]
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
        "type",
        "attendee_limit",
    ]
    actions = [make_public, make_not_public, workshop_update_from_pretalx]

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
