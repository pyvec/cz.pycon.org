from django.urls import re_path

from announcements.views import announcement_list

urlpatterns = [
    re_path("^$", announcement_list, name="announcements_list"),
]
