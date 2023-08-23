from django.db import models
from django.utils.text import slugify
from wagtail.models import Page


class Level(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=False, blank=True)
    order = models.PositiveIntegerField(help_text="display order on front end (lower the number, the higher it is)")
    size = models.PositiveIntegerField(default=0, help_text="visual size (lower the number, the bigger it is)")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Level, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order', 'title']


class Sponsor(models.Model):
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True)

    name = models.CharField(max_length=200, unique=True)
    logo = models.FileField(null=True, blank=True, help_text="SVG only")

    description = models.TextField(
        null=True, blank=True, help_text="markdown formatted"
    )
    link_url = models.URLField()
    twitter = models.URLField(null=True, blank=True, help_text="full URL")
    facebook = models.URLField(null=True, blank=True, help_text="full URL")
    linkedin = models.URLField(null=True, blank=True, help_text="full URL")

    published = models.BooleanField(default=False)

    class Meta:
        ordering = ["level", "name"]

    def __str__(self):
        return self.name

    @property
    def slug(self):
        return slugify(self.name)
