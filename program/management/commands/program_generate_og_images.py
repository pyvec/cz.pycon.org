import os
import pathlib
from typing import Type

from django.conf import settings
from django.core.management.base import BaseCommand

from program import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        # `og_image_generator` depends on playwright, which is not installed
        # in production. We should delay its import to the last possible moment.
        from program import og_image_generator

        # Playwright library creates an async loop in the current thread.
        # Because of this, Django thinks that we are running in an async context
        # and prevents us from running database queries.
        #
        # We set this env. variable to suppress the error, because the command's code
        # does not actually run in the async context.
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "1"

        media_root = pathlib.Path(settings.MEDIA_ROOT)
        og_root = media_root / "og-images"

        with og_image_generator.OgImageGenerator() as generator:
            self._generate_og_images(
                generator=generator,
                model_type=models.Talk,
                template_name="program/og_images/talk.html",
                output_path=og_root / "talks",
            )
            self._generate_og_images(
                generator=generator,
                model_type=models.Workshop,
                template_name="program/og_images/workshop.html",
                output_path=og_root / "workshops",
            )

    def _generate_og_images(
        self,
        generator,
        model_type: Type[models.Session],
        template_name: str,
        output_path: pathlib.Path,
    ) -> None:
        """
        Generates image for each object from the database and prints progress.
        """
        objects = model_type.objects.filter(is_public=True)
        self.stdout.write(
            f"Generating OG images for {len(objects)} "
            f"{model_type._meta.verbose_name_plural}",
        )
        for obj in objects:
            result = generator.generate_image(
                template_name=template_name,
                context={
                    "session": obj,
                },
                output_path=output_path / f"{obj.type}-{obj.id}.jpg",
            )
            self.stdout.write(f"  generated {result.relative_to(settings.BASE_DIR)}")
