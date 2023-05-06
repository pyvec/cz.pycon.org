from django.db import models
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class Sponsor(models.Model):
    LEVELS = (
        (1, "Platinum"),
        (2, "Gold"),
        (3, "Silver"),
        (4, "Bronze"),
        (5, "Diversity"),
        (6, "Media"),
        (7, "Partners"),
        (9, "Connectivity"),
    )

    level = models.IntegerField(choices=LEVELS, default=3)

    name = models.CharField(max_length=200, unique=True)
    logo = models.FileField(null=True, blank=True, help_text="SVG only")

    description = models.TextField(
        null=True, blank=True, help_text="markdown formatted"
    )
    link_url = models.URLField()
    twitter = models.URLField(null=True, blank=True, help_text="full URL")
    facebook = models.URLField(null=True, blank=True, help_text="full URL")

    published = models.BooleanField(default=False)

    class Meta:
        ordering = ["level", "name"]

    def __str__(self):
        return self.name

    @property
    def slug(self):
        return slugify(self.name)


class SponsorsOffer(Page):
    about = RichTextField(blank=True)
    benefits = RichTextField(blank=True)
    event_summary = RichTextField(blank=True)
    custom_sponsorship = RichTextField(blank=True)
    contacts = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("about"),
        FieldPanel("benefits"),
        FieldPanel("event_summary"),
        FieldPanel("custom_sponsorship"),
        FieldPanel("contacts"),
    ]
