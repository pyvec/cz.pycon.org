from django.contrib import admin

from .models import Organizer


class OrganizerAdmin(admin.ModelAdmin):
    list_display = [
        "full_name",
        "published",
    ]
    list_editable = [
        "published",
    ]
    list_filter = [
        "published",
    ]


admin.site.register(Organizer, OrganizerAdmin)
