from django.db import models


class Speaker(models.Model):
    full_name = models.CharField(max_length=200)
    bio = models.TextField()
    short_bio = models.TextField(blank=True, help_text="for keynote speakers")
    twitter = models.CharField(max_length=255, blank=True)
    github = models.CharField(max_length=255, blank=True)
    email = models.EmailField()
    photo = models.ImageField()
    talks = models.ManyToManyField("Talk", blank=True, related_name="talk_speakers")
    workshops = models.ManyToManyField(
        "Workshop", blank=True, related_name="workshop_speakers"
    )
    display_position = models.PositiveSmallIntegerField(
        default=0, help_text="sort order on frontend displays"
    )
    is_public = models.BooleanField(default=True)


class Session(models.Model):
    """Base class with common fields for 'Workshop' and 'Talk'."""

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["is_public"]),
            models.Index(fields=["is_backup"]),
            models.Index(fields=["type"]),
        ]
        ordering = ("order",)

    TYPE = (("workshop", "Workshop"), ("sprint", "Sprint"), ("talk", "Talk"))
    LANGUAGES = (
        ("en", "English (preferred)"),
        ("cs", "Czech/Slovak"),
    )
    DIFFICULTY = (
        ("beginner", "Beginner"),
        ("advanced", "Advanced"),
    )

    type = models.CharField(max_length=10, choices=TYPE)
    language = models.CharField(max_length=2, choices=LANGUAGES, default="en")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY, default="beginner")
    order = models.SmallIntegerField(
        unique=True, help_text="display order on front-end"
    )
    title = models.CharField(max_length=250)
    abstract = models.TextField()
    is_backup = models.BooleanField(default=False, blank=True)
    is_public = models.BooleanField(default=False, blank=True)
    in_data_track = models.BooleanField("PyData Track", default=False, blank=True)
    private_note = models.TextField(
        default="", blank=True, help_text="DO NOT SHOW ON WEBSITE"
    )
    og_image = models.ImageField(
        null=True,
        blank=True,
        help_text="og:image (social media image) 1200×630 pixels",
    )


class Talk(Session):
    video_id = models.CharField(
        max_length=100, default="", blank=True, help_text="YouTube URL"
    )
    is_keynote = models.BooleanField(default=False, blank=True)


class Workshop(Session):
    LENGTH = (
        ("1h", "1 hour"),
        ("2h", "2 hours"),
        ("3h", "3 hours"),
        ("1d", "Full day (most sprints go here!)"),
        ("xx", "Something else! (Please leave a note in the abstract!)"),
    )
    REGISTRATION = (
        ("without", "Without"),
        ("free", "Free"),
        ("paid", "Paid"),
    )

    requirements = models.TextField(
        "What should attendees bring, install and know?",
        default="",
        blank=True,
        help_text="include even the most obvious stuff: laptops, GIT, Python",
    )
    length = models.CharField(
        max_length=2,
        choices=LENGTH,
        blank=True,
    )
    registration = models.CharField(
        max_length=10, choices=REGISTRATION, default="free", blank="free"
    )
    is_sold_out = models.BooleanField("Sold out", default=False, blank=True)
    attendee_limit = models.PositiveSmallIntegerField(
        "Attendee limit",
        default=False,
        blank=True,
        help_text="maximum number of attendees allowed",
    )
