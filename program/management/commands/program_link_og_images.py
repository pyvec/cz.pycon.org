import pathlib
import re
from functools import cached_property
from typing import Type

from django.conf import settings
from django.core.management.base import BaseCommand

from program import models


class Command(BaseCommand):
    @cached_property
    def og_image_regex(self) -> re.Pattern:
        # Examples: talk-42.jpg
        #           talk-42.b0d4f9bb088a.jpg
        return re.compile("^\w+-(?P<id>\d+)\..*")

    def handle(self, og_images_dir: str = "og-images", *args, **options):
        media_path = pathlib.Path(settings.MEDIA_ROOT)

        self._link_images_to_model(
            path=media_path / og_images_dir / "talks",
            model_type=models.Talk,
        )
        self._link_images_to_model(
            path=media_path / og_images_dir / "workshops",
            model_type=models.Workshop,
        )

    def _link_images_to_model(
        self, path: pathlib.Path, model_type: Type[models.Session]
    ) -> None:
        og_images_by_id = self._scan_images_in_dir(path)
        if not og_images_by_id:
            return
        processed = self._link_session_images(og_images_by_id, model_type)
        self.stdout.write(
            f"Linked {processed} images to {model_type._meta.verbose_name_plural}"
        )

    def _scan_images_in_dir(self, path: pathlib.Path) -> dict[int, pathlib.Path]:
        if not path.exists():
            self.stderr.write(
                f"No OG images found at {path}, generate some first "
                f"using `make generate-og-images`"
            )
            return {}

        result = {}
        all_files: list[pathlib.Path] = list(path.glob("*.jpg"))
        mtimes = {file: file.stat().st_mtime for file in all_files}
        all_files.sort(key=lambda file: mtimes[file])

        for file in all_files:
            if not (match := self.og_image_regex.match(file.name)):
                continue

            result[int(match.group("id"))] = file.relative_to(settings.MEDIA_ROOT)

        return result

    def _link_session_images(
        self, images_by_id: dict[int, pathlib.Path], model_type: Type[models.Session]
    ) -> int:
        processed = 0
        sessions: dict[int, models.Session] = model_type.objects.in_bulk(
            images_by_id.keys()
        )
        for model_id, image_path in images_by_id.items():
            # Skip images that does not match a record from the database
            if model_id not in sessions:
                continue
            sessions[model_id].og_image = image_path
            processed += 1
        model_type.objects.bulk_update(
            objs=sessions.values(),
            fields=["og_image"],
        )
        return processed
