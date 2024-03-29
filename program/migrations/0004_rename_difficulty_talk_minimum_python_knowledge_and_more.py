# Generated by Django 4.2.1 on 2023-07-31 19:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("program", "0003_alter_talk_difficulty_alter_workshop_difficulty"),
    ]

    operations = [
        migrations.RenameField(
            model_name="talk",
            old_name="difficulty",
            new_name="minimum_python_knowledge",
        ),
        migrations.RenameField(
            model_name="workshop",
            old_name="difficulty",
            new_name="minimum_python_knowledge",
        ),
        migrations.RemoveField(
            model_name="talk",
            name="in_data_track",
        ),
        migrations.RemoveField(
            model_name="workshop",
            name="in_data_track",
        ),
        migrations.AddField(
            model_name="speaker",
            name="linkedin",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="speaker",
            name="personal_website",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="talk",
            name="minimum_topic_knowledge",
            field=models.CharField(
                choices=[
                    ("few-times", "Attendees who used it few times"),
                    ("regular-basis", "Attendees who use it on a regular basis"),
                    ("no-previous-knowledge", "No previous knowledge needed"),
                ],
                default="no-previous-knowledge",
                max_length=256,
            ),
        ),
        migrations.AddField(
            model_name="talk",
            name="track",
            field=models.CharField(
                choices=[
                    ("pydata", "PyData"),
                    ("beginners", "Beginners"),
                    ("general", "General"),
                ],
                default="beginner",
                max_length=16,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="workshop",
            name="minimum_topic_knowledge",
            field=models.CharField(
                choices=[
                    ("few-times", "Attendees who used it few times"),
                    ("regular-basis", "Attendees who use it on a regular basis"),
                    ("no-previous-knowledge", "No previous knowledge needed"),
                ],
                default="no-previous-knowledge",
                max_length=256,
            ),
        ),
        migrations.AddField(
            model_name="workshop",
            name="track",
            field=models.CharField(
                choices=[
                    ("pydata", "PyData"),
                    ("beginners", "Beginners"),
                    ("general", "General"),
                ],
                default="beginner",
                max_length=16,
            ),
            preserve_default=False,
        ),
    ]
