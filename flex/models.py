from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from . import blocks


class FlexPage(Page):
    template = "flex/flex_page.html"

    subtitle = models.CharField(max_length=100, blank=True, null=True)

    body = StreamField(
        [
            ("rich_text", blocks.RichTextBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("body"),
    ]

    class Meta:
        verbose_name = "Flex Page"
        verbose_name_plural = "Flex Pages"
