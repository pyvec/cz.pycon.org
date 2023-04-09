from django.urls import re_path

from team.views import team_list

urlpatterns = [
    re_path("^$", team_list, name="team_list"),
]
