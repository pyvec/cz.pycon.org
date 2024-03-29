# Generated by Django 4.2.1 on 2023-08-28 16:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("program", "0015_alter_speaker_photo"),
    ]

    operations = [
        migrations.CreateModel(
            name="Utility",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Title")),
                ("description", models.TextField(blank=True, null=True)),
                ("url", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "is_streamed",
                    models.BooleanField(
                        blank=True,
                        default=False,
                        verbose_name="Is streamed to other rooms",
                    ),
                ),
            ],
            options={
                "verbose_name": "Utility",
                "verbose_name_plural": "Utilities",
                "ordering": ("title", "id"),
            },
        ),
    ]
