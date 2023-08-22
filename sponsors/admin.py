from django.contrib import admin
from django.utils.html import format_html

from sponsors.models import Sponsor, Level


class SponsorAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "level",
        "get_link",
        "published",
    ]
    list_display_links = [
        "name",
    ]
    list_editable = [
        "published",
    ]
    list_filter = [
        "published",
        "level",
    ]

    def get_link(self, instance):
        return format_html('<a href="{url}">{url}</a>', url=instance.link_url)

    get_link.short_description = "link"


admin.site.register(Sponsor, SponsorAdmin)
admin.site.register(Level)
