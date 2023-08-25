from django.contrib import admin

from announcements.models import Announcement


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        "message",
        "order",
        "size",
        "is_public",
    )
    list_filter = ("is_public",)
    list_editable = (
        "order",
        "is_public",
        "size",
    )


admin.site.register(Announcement, AnnouncementAdmin)
