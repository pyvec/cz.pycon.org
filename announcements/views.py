from django.template.response import TemplateResponse

from announcements.models import Announcement


def announcement_list(request):
    announcements = Announcement.objects.all()
    return TemplateResponse(
        request, "announcements/archive.html", {"announcements": announcements}
    )
