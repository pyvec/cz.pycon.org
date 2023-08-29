from typing import Any

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from program import pretalx


class Speaker(models.Model):
    PRETALX_FIELDS = [
        "full_name",
        "bio",
        "email",
        "personal_website",
        "github",
        "twitter",
        "linkedin",
    ]
    """List of fields synced from pretalx."""

    class Meta:
        ordering = ("order",)

    full_name = models.CharField(max_length=200)
    bio = models.TextField()
    short_bio = models.TextField(blank=True, help_text="for keynote speakers")
    twitter = models.URLField(max_length=255, blank=True)
    github = models.URLField(max_length=255, blank=True)
    linkedin = models.URLField(max_length=255, blank=True)
    personal_website = models.URLField(max_length=255, blank=True)
    email = models.EmailField()
    photo = models.ImageField(null=True, blank=True, upload_to="speakers/")
    talks = models.ManyToManyField("Talk", blank=True, related_name="talk_speakers")
    workshops = models.ManyToManyField("Workshop", blank=True, related_name="workshop_speakers")
    order = models.PositiveSmallIntegerField(default=500, help_text="display order on front end (lower the number, higher it is)")
    is_public = models.BooleanField(default=True)
    pretalx_code = models.CharField(max_length=16, null=True, blank=True, unique=True, )
    """
    Code of the speaker in pretalx. Will be used for synchronization.
    When not set, this speaker will not be synchronized with pretalx.
    """

    def __str__(self) -> str:
        return self.full_name

    def update_from_pretalx(self, pretalx_speaker: dict[str, Any]) -> None:
        # Note: remember to update the PRETALX_FIELDS class variable
        # when adding/removing fields synced with pretalx.
        self.full_name = pretalx_speaker["name"]
        self.bio = (
            pretalx_speaker["biography"]
            if pretalx_speaker["biography"] is not None
            else ""
        )
        self.email = pretalx_speaker["email"]

        answers = pretalx.AnswersCollection(pretalx_speaker["answers"])
        self.personal_website = answers.get_answer("Your personal website")
        self.github = answers.get_answer("Your GitHub")
        self.twitter = answers.get_answer("Your Twitter")
        self.linkedin = answers.get_answer("Your LinkedIn")


class Session(models.Model):
    """Base class with common fields for 'Workshop' and 'Talk'."""

    PRETALX_FIELDS = [
        "title",
        "abstract",
        "private_note",
        "track",
        "language",
        "minimum_python_knowledge",
        "minimum_topic_knowledge",
        "type",
    ]
    """List of fields synced from pretalx."""

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["is_public"]),
            models.Index(fields=["is_backup"]),
            models.Index(fields=["type"]),
        ]
        ordering = ("order",)

    TYPE = (("workshop", "Workshop"), ("sprint", "Sprint"), ("talk", "Talk"), ("panel", "Panel"))

    PRETALX_TYPE_MAP = {
        "talk": "talk",
        "panel": "panel",
        "keynote": "talk",
        "workshop": "workshop",
        "workshop full day": "workshop",
    }

    LANGUAGES = (
        ("en", "English"),
        ("cs", "Czech/Slovak"),
    )

    PRETALX_LANGUAGE_MAP = {
        "czech or slovak (preferred for beginners track)": "cs",
        "english (preferred for the rest of talks and workshops)": "en",
    }

    DIFFICULTY = (
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    )

    PRETALX_DIFFICULTY_MAP = {
        "beginner: can write simple scripts (typical attendee of our beginner’s track)": "beginner",
        "intermediate: uses frameworks and third-party libraries": "intermediate",
        "advanced: understands advanced python concepts, such as generators and comprehensions, async/await, advanced usage of classes": "advanced",
    }

    TRACK = (
        ("general", "General"),
        ("pydata", "PyData"),
        ("beginners", "Beginners"),
        ("keynote", "Keynote"),
    )

    TOPIC_KNOWLEDGE = (
        ("no-previous-knowledge", "No previous knowledge needed"),
        ("few-times", "Attendees who used it few times"),
        ("regular-basis", "Attendees who use it on a regular basis"),
    )

    PRETALX_TOPIC_KNOWLEDGE_MAP = {
        "no previous knowledge is required: you will explain basic concepts and problems it solves": "no-previous-knowledge",
        "attendees who used it just a few times": "few-times",
        "attendees who use it on a regular basis": "regular-basis",
    }

    type = models.CharField(max_length=10, choices=TYPE)
    language = models.CharField(max_length=2, choices=LANGUAGES, default="en")
    minimum_python_knowledge = models.CharField(
        max_length=16, choices=DIFFICULTY, default="beginner"
    )
    minimum_topic_knowledge = models.CharField(
        max_length=256, choices=TOPIC_KNOWLEDGE, default="no-previous-knowledge"
    )
    track = models.CharField(max_length=16, choices=TRACK)
    order = models.PositiveSmallIntegerField(default=500, help_text="display order on front end (lower the number, higher it is)", )
    title = models.CharField(max_length=250)
    abstract = models.TextField()
    is_backup = models.BooleanField(default=False, blank=True)
    is_public = models.BooleanField(default=False, blank=True)
    private_note = models.TextField(
        default="", blank=True, help_text="DO NOT SHOW ON WEBSITE"
    )
    og_image = models.ImageField(
        null=True,
        blank=True,
        help_text="og:image (social media image) 1200×630 pixels",
        upload_to="og-images/program/"
    )
    pretalx_code = models.CharField(
        max_length=16, null=True, blank=True, unique=True
    )
    """
    Code of the submission in pretalx. Will be used for synchronization.
    When not set, this submission (workshop or talk) will not be synchronized with pretalx.
    """

    @classmethod
    def get_pretalx_submission_type(cls, submission_type: dict[str, str]) -> str:
        return cls.PRETALX_TYPE_MAP.get(submission_type["en"].casefold(), "talk")

    def get_absolute_url(self) -> str:
        return reverse("program:session_detail", kwargs={
            "type": self.type,
            "session_id": self.id,
        })

    def __str__(self) -> str:
        return self.title

    def update_from_pretalx(self, pretalx_submission: dict[str, Any]) -> None:
        # Note: remember to update the PRETALX_FIELDS class variable
        # when adding/removing fields synced with pretalx.
        self.title = pretalx_submission["title"]
        self.abstract = pretalx_submission["description"]
        self.private_note = pretalx_submission["internal_notes"]
        self.track = pretalx_submission["track"]["en"].casefold()

        answers = pretalx.AnswersCollection(pretalx_submission["answers"])
        self.language = answers.get_mapped_answer(
            question_text="Language of your session",
            value_map=self.PRETALX_LANGUAGE_MAP,
        )
        self.minimum_python_knowledge = answers.get_mapped_answer(
            question_text="Minimum recommended Python knowledge",
            value_map=self.PRETALX_DIFFICULTY_MAP,
        )
        self.minimum_topic_knowledge = answers.get_mapped_answer(
            question_text="Minimum recommended topic knowledge",
            value_map=self.PRETALX_TOPIC_KNOWLEDGE_MAP,
        )

        if not self.type:
            self.type = self.get_pretalx_submission_type(
                pretalx_submission["submission_type"]
            )


class Talk(Session):
    PRETALX_FIELDS = Session.PRETALX_FIELDS + ["is_keynote"]

    video_id = models.CharField(
        max_length=100, default="", blank=True, help_text="YouTube ID (from URL)"
    )
    is_keynote = models.BooleanField(default=False, blank=True)

    @property
    def speakers(self):
        # To improve query performance when rendering schedule, speakers will be
        # prefetched to `public_speakers` attr as a list. Use this list when possible.
        if hasattr(self, "public_speakers"):
            return self.public_speakers
        return self.talk_speakers.all().filter(is_public=True)

    def update_from_pretalx(self, pretalx_submission: dict[str, Any]) -> None:
        # Note: remember to update the PRETALX_FIELDS class variable
        # when adding/removing fields synced with pretalx.
        super().update_from_pretalx(pretalx_submission)
        self.is_keynote = (
                pretalx_submission["submission_type"]["en"].casefold() == "keynote"
        )


class Workshop(Session):
    PRETALX_FIELDS = Session.PRETALX_FIELDS + [
        "requirements",
        "length",
        "attendee_limit",
    ]

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

    @property
    def speakers(self):
        # To improve query performance when rendering schedule, speakers will be
        # prefetched to `public_speakers` attr as a list. Use this list when possible.
        if hasattr(self, "public_speakers"):
            return self.public_speakers
        return self.workshop_speakers.all().filter(is_public=True)

    def update_from_pretalx(self, pretalx_submission: dict[str, Any]) -> None:
        # Note: remember to update the PRETALX_FIELDS class variable
        # when adding/removing fields synced with pretalx.
        super().update_from_pretalx(pretalx_submission)

        answers = pretalx.AnswersCollection(pretalx_submission["answers"])
        self.requirements = answers.get_answer("Prerequisties and Requirements")

        if not self.length:
            duration_minutes = pretalx_submission["duration"]
            duration_hours = round(duration_minutes / 60)
            if duration_hours > 3:
                self.length = "1d"
            elif 3 >= duration_hours >= 1:
                self.length = f"{duration_hours}h"

        if not self.attendee_limit:
            participants_str = answers.get_answer("Number of participants")
            try:
                self.attendee_limit = int(participants_str) if participants_str else 0
            except ValueError:
                self.attendee_limit = 0


class Utility(models.Model):
    title = models.CharField(max_length=255, verbose_name='Title')
    slug = models.SlugField(max_length=50, default="")
    description = models.TextField(blank=True, null=True, help_text="markdown formatted")
    url = models.CharField(max_length=255, blank=True, null=True, verbose_name="URL", help_text="whole item will be a link to this URL")
    is_streamed = models.BooleanField('Is streamed to other rooms', default=False, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Utility'
        verbose_name_plural = 'Utilities'
        ordering = ('title', 'id',)


class Room(models.Model):
    label = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    order = models.PositiveSmallIntegerField(default=50, help_text="display order on front end (lower the number, higher it is)")

    def __str__(self):
        return self.label

    class Meta:
        ordering = ('order', 'id',)


class Slot(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()

    talk = models.ForeignKey(Talk, on_delete=models.SET_NULL, blank=True, null=True)
    workshop = models.ForeignKey(Workshop, on_delete=models.SET_NULL, blank=True, null=True)
    utility = models.ForeignKey(Utility, on_delete=models.SET_NULL, blank=True, null=True)

    room = models.ForeignKey(Room, on_delete=models.SET_NULL, blank=True, null=True)

    def clean(self):
        # check that only one of the options is set
        msg = 'Only one of "talk", "workshop" or "utility" per slot.'
        fields = 'talk', 'workshop', 'utility'
        if tuple(getattr(self, field) for field in fields).count(None) < 2:
            raise ValidationError({f: msg for f in fields})

    @property
    def event(self):
        return self.talk or self.workshop or self.utility

    def __str__(self):
        start = self.start.strftime('%d/%m/%y %H:%M')
        end = self.end.strftime('%d/%m/%y %H:%M')
        return f'{self.event} FROM {start} TO {end} IN {self.room}'

    class Meta:
        ordering = ('start', 'room',)
