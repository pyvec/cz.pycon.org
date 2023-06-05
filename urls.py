"""pycon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path(
        "2023/",
        include(
            [
                path("", TemplateView.as_view(template_name='pages/homepage.html'), name='homepage'),
                path("coc/", TemplateView.as_view(template_name='pages/coc.html'), name='coc'),
                path("privacy-policy/", TemplateView.as_view(template_name='pages/privacy_policy.html'), name='privacy_policy'),
                path("cfp/", TemplateView.as_view(template_name='pages/cfp.html'), name='cfp'),
                path("cfp-guide/", TemplateView.as_view(template_name='pages/cfp_guide.html'), name='cfp_guide'),
                path("cfp-pruvodce/", TemplateView.as_view(template_name='pages/cfp_pruvodce.html'), name='cfp_pruvodce'),
                path("pattern-lib/", TemplateView.as_view(template_name='pages/pattern_lib.html'), name='pattern_lib'),

                path("admin/", admin.site.urls),
                path("wagtail/", include("wagtail.admin.urls")),
                path("team/", include("team.urls")),
                path("sponsors/", include("sponsors.urls")),
                path("announcements/", include("announcements.urls")),
                path("program/", include("program.urls")),
                path("intermissions/", include("intermissions.urls")),
            ]
        ),
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
