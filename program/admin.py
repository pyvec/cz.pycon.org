from django.contrib import admin

from program.models import Speaker, Talk, Workshop

admin.site.register(Speaker)
admin.site.register(Talk)
admin.site.register(Workshop)
