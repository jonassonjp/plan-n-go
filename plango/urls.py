"""
Plan N'Go — URLs principais
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from plango.views import index

urlpatterns = [
    path("admin/",       admin.site.urls),
    path("",             index,           name="index"),
    path("accounts/",    include("accounts.urls")),
    path("destinations/", include("destinations.urls")),
    path("lists/",       include("lists.urls")),
    path("itineraries/", include("itineraries.urls")),
    path("feed/",        include("feed.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
