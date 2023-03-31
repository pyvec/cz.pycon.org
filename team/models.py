from django.db import models


class Organizer(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField(default="", blank=True, help_text="This field is private")
    twitter = models.CharField(max_length=255, blank=True, help_text="handle without @")
    github = models.CharField(max_length=255, blank=True, help_text="handle only")
    photo = models.ImageField(upload_to="team/photos")

    published = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name
