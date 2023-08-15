from django.conf import settings
from django.urls import re_path, path
from django.views.generic import RedirectView

from .views import (
    preview,
    talks_list,
    workshops_list,
    debug_og_image_for_talk,
    debug_og_image_for_workshop,
)

app_name = "program"

urlpatterns = [
    re_path("^$", RedirectView.as_view(pattern_name="program:talks_list")),
    re_path("^talks/$", talks_list, name="talks_list"),
    re_path("^workshops/$", workshops_list, name="workshops_list"),
    re_path("^preview/$", preview, name="preview"),
]

# Routes for previewing OG images template.
# Activated only in DEBUG mode.
if settings.DEBUG:
    urlpatterns += [
        path("og-image/talks/<int:session_id>", debug_og_image_for_talk),
        path("og-image/workshops/<int:session_id>", debug_og_image_for_workshop),
    ]
