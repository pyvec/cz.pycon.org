from django.urls import re_path

from .views import announcements, index, slido, sponsors

urlpatterns = [
    re_path("^$", index, name="cycle_all"),
    re_path("^sponsors/(?P<level>[\w\-]+)/$", sponsors, name="sponsors"),
    re_path("^announcements/$", announcements, name="announcements"),
    re_path("^slido/$", slido, name="slido"),
]
