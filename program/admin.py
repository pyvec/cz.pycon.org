from django.contrib import admin

from program.models import Speaker, Talk, Workshop


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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related("talk_speakers")
        return qs

    @admin.display(description="Speakers", empty_value="not set")
    def speakers(self, talk: Talk) -> str:
        return ", ".join(speaker.full_name for speaker in talk.talk_speakers.all())


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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related("workshop_speakers")
        return qs

    @admin.display(description="Speakers", empty_value="not set")
    def speakers(self, workshop: Workshop) -> str:
        return ", ".join(
            speaker.full_name for speaker in workshop.workshop_speakers.all()
        )
