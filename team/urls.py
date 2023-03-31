from django.urls import re_path

from .views import team_list

urlpatterns = [re_path("^$", team_list, name="team_list")]
