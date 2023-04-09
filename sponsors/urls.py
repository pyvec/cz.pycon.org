from django.urls import re_path

from sponsors.views import sponsors_list, sponsors_offer

urlpatterns = [
    re_path("^$", sponsors_list, name="sponsors_list"),
    re_path(r"^offer/$", sponsors_offer, name="sponsors_offer"),
]
