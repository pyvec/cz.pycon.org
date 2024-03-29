# Generated by Django 4.2.1 on 2023-08-07 08:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("program", "0006_speaker_pretalx_code_session_pretalx_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="talk",
            name="order",
            field=models.SmallIntegerField(
                default=500, help_text="display order on front-end"
            ),
        ),
        migrations.AlterField(
            model_name="workshop",
            name="order",
            field=models.SmallIntegerField(
                default=500, help_text="display order on front-end"
            ),
        ),
    ]
