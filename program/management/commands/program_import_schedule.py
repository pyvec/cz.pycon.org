import collections
from argparse import ArgumentParser

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Import schedule from an XLSX file - creates slots in local database "
        "and writes a JSON file for loaddata. This command also creates rooms "
        "and utilities when required."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--xlsx", "-i", default="data/schedule.xlsx")
        parser.add_argument("--output", "-o", default="data/slots.json")

    def handle(self, xlsx: str, output: str, *args, **options) -> None:
        # Lazy imports to save a bit of memory.
        from django.core import serializers

        from program.schedule_import import ScheduleImporter

        importer = ScheduleImporter()
        new_objects = importer.import_xlsx(xlsx)
        data = serializers.serialize("json", new_objects)
        with open(output, "w", encoding="utf-8") as output_file:
            output_file.write(data)

        imported_counts = collections.Counter(type(obj) for obj in new_objects)
        self.stdout.write(f"Schedule imported, generated {output} with:")
        for model_type, count in imported_counts.items():
            self.stdout.write(f"  {count} {model_type._meta.verbose_name_plural}")
