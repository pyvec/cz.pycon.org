from django.db import models


class Announcement(models.Model):
    SIZES = [
        (1, "Large"),
        (2, "Medium"),
        (3, "Small"),
        (4, "Extra Small"),
    ]

    message = models.TextField(help_text="markdown formatted")
    position = models.PositiveSmallIntegerField(default=0)
    is_public = models.BooleanField(default=False)
    font_size = models.PositiveSmallIntegerField(choices=SIZES, default=1)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.message[:30] + "…" if len(self.message) > 30 else self.message
