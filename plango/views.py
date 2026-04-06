"""
Plan N'Go — Views principais
"""

from django.shortcuts import render
from feed.models import FeaturedDestination


def index(request):
    featured = FeaturedDestination.objects.filter(
        is_active=True
    ).order_by("order", "name")

    return render(request, "plango/index.html", {
        "featured_destinations": featured,
    })
