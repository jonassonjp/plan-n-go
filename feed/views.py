"""
Plan N'Go — Views do app feed
"""

from django.shortcuts import render, get_object_or_404
from .models import FeaturedDestination


def destination_detail(request, slug):
    """Página de detalhes de um destino em destaque."""
    dest = get_object_or_404(FeaturedDestination, slug=slug, is_active=True)
    return render(request, "feed/destination_detail.html", {"dest": dest})
