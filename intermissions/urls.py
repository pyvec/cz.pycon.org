from django.urls import path

from .views import announcements, index, slido, sponsors, next_talk

urlpatterns = [
    path("", index, name="cycle_all"),
    path("sponsors/<level>/", sponsors, name="sponsors"),
    path("announcements/", announcements, name="announcements"),
    path("slido/", slido, name="slido"),
    path("next-talk/<int:page>", next_talk, name="next_talk"),
]
