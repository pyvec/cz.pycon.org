from django.db import models


class Announcement(models.Model):
    SIZES = [
        (1, "Extra Large"),
        (2, "Large"),
        (3, "Medium"),
        (4, "Small"),
        (5, "Extra Small"),
    ]

    is_public = models.BooleanField(default=False)
    message = models.TextField(help_text="Markdown flavoured")
    order = models.PositiveSmallIntegerField(default=50)
    size = models.PositiveSmallIntegerField(choices=SIZES, default=3)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.message[:30] + "…" if len(self.message) > 30 else self.message
