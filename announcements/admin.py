from django.contrib import admin

from announcements.models import Announcement


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        "message",
        "position",
        "is_public",
        "font_size",
    )
    list_filter = ("is_public",)
    list_editable = (
        "position",
        "is_public",
    )


admin.site.register(Announcement, AnnouncementAdmin)
