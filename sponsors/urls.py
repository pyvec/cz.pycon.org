from django.urls import re_path

from sponsors.views import sponsors_list

urlpatterns = [
    re_path("^$", sponsors_list, name="sponsors_list"),
]
