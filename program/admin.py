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


@admin.action(description="Update from pretalx")
def speaker_update_from_pretalx(modeladmin, request, queryset):
    sync = create_pretalx_sync()
    with transaction.atomic():
        sync.update_speakers(queryset)


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "is_public", "display_position", "pretalx_code"]
    search_fields = ["full_name", "email"]
    ordering = ["full_name"]
    fields = [
        "pretalx_code",
        "is_public",
        "display_position",
        "photo",
        "talks",
        "workshops",
        "bio",
        "short_bio",
        "twitter",
        "github",
        "linkedin",
        "personal_website",
        "email",
    ]
    readonly_fields = [
        "full_name",
        "email",
        "bio",
        "twitter",
        "github",
        "linkedin",
        "personal_website",
    ]
    actions = [make_public, speaker_update_from_pretalx]


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
    fields = [
        "pretalx_code",
        "is_public",
        "order",
        "is_backup",
        "og_image",
        "video_id",
        "private_note",
        "language",
        "track",
        "type",
        "minimum_python_knowledge",
        "minimum_topic_knowledge",
        "is_keynote",
        "abstract",
    ]
    readonly_fields = [
        "title",
        "speakers",
        "is_keynote",
        "abstract",
        "track",
        "language",
        "minimum_python_knowledge",
        "minimum_topic_knowledge",
        "type",
    ]
    actions = [make_public, talk_update_from_pretalx]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related("talk_speakers")
        return qs

    @admin.display(description="Speakers", empty_value="not set")
    def speakers(self, talk: Talk) -> str:
        return ", ".join(speaker.full_name for speaker in talk.talk_speakers.all())


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
    search_fields = ["title", "abstract", "workshop_speakers__full_name", "pretalx_code"]
    ordering = ["is_backup", "track", "order", "title"]
    fields = [
        "pretalx_code",
        "is_public",
        "order",
        "is_sold_out",
        "og_image",
        "registration",
        "length",
        "is_backup",
        "private_note",
        "language",
        "track",
        "type",
        "minimum_python_knowledge",
        "minimum_topic_knowledge",
        "abstract",
        "requirements",
        "attendee_limit",

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
    actions = [make_public, workshop_update_from_pretalx]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related("workshop_speakers")
        return qs

    @admin.display(description="Speakers", empty_value="not set")
    def speakers(self, workshop: Workshop) -> str:
        return ", ".join(
            speaker.full_name for speaker in workshop.workshop_speakers.all()
        )
