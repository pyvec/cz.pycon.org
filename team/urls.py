from django.urls import include, re_path

from .views import team_list

urlpatterns = [
    re_path("^$", team_list, name="team_list"),
    re_path(r"^wagtail/", include("wagtail.admin.urls")),
]
