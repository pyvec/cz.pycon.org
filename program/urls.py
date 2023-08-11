from django.urls import re_path
from django.views.generic import RedirectView

from .views import preview, talks_list, workshops_list

app_name = "program"

urlpatterns = [
    re_path("^$", RedirectView.as_view(pattern_name="program:talks_list")),
    re_path("^talks/$", talks_list, name="talks_list"),
    re_path("^workshops/$", workshops_list, name="workshops_list"),
    re_path("^preview/$", preview, name="preview"),
]
