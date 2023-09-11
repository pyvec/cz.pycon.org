from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class Organizer(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField(default="", blank=True, help_text="private field")
    twitter = models.URLField(null=True, blank=True, help_text="full URL")
    github = models.URLField(null=True, blank=True, help_text="full URL")
    linkedin = models.URLField(null=True, blank=True, help_text="full URL")
    photo = models.ImageField(upload_to="organizers/")
    published = models.BooleanField(default=False)


@receiver(post_save, sender=Organizer)
def log_image_path(sender, instance, **kwargs):
    print(f"Image saved at: {instance.photo.path}")


class TeamPage(Page):
    content = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("content")]
