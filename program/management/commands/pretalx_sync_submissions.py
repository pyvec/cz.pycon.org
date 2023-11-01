from django.core.management.base import BaseCommand

from program import pretalx, pretalx_sync


class Command(BaseCommand):
    def handle(self, *args, **options):
        pretalx_client = pretalx.create_pretalx_client()
        sync = pretalx_sync.PretalxSync(pretalx_client)
        sync.full_sync()
