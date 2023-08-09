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
    self.message_user(request, f"Selected items have been made public.")


@admin.action(description="Update from pretalx")
def speaker_update_from_pretalx(modeladmin, request, queryset):
    sync = create_pretalx_sync()
    with transaction.atomic():
        sync.update_speakers(queryset)


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "is_public", "pretalx_code"]
    search_fields = ["full_name", "email"]
    ordering = ["full_name"]
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
    ]
    list_filter = ["is_keynote", "track", "language", "is_public", "is_backup"]
    search_fields = ["title", "abstract", "talk_speakers__full_name"]
    ordering = ["title"]
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
    ]
    list_filter = ["type", "track", "language", "is_public", "is_backup"]
    search_fields = ["title", "abstract", "workshop_speakers__full_name"]
    ordering = ["title"]
    readonly_fields = [
        "title",
        "speakers",
        "abstract",
        "track",
        "language",
        "minimum_python_knowledge",
        "minimum_topic_knowledge",
        "type",
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
