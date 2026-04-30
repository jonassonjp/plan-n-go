"""
Plan N'Go — Views do app feed
"""

from django.shortcuts import render, get_object_or_404
from .models import FeaturedDestination
from destinations.models import Destination
from roteiros.models import Roteiro


def feed_view(request):
    tab = request.GET.get("tab", "destinos")
    continente = request.GET.get("continente", "")

    destinos = Destination.objects.filter(
        visibility=Destination.VISIBILITY_PUBLIC,
        status=Destination.STATUS_ACTIVE,
    ).select_related("user").order_by("-updated_at")

    if continente:
        destinos = destinos.filter(continent=continente)

    roteiros = Roteiro.objects.filter(
        visibility=Roteiro.VISIBILITY_PUBLIC,
    ).select_related("user", "destination").order_by("-updated_at")

    continentes = (
        Destination.objects
        .filter(visibility=Destination.VISIBILITY_PUBLIC, status=Destination.STATUS_ACTIVE)
        .exclude(continent="")
        .values_list("continent", flat=True)
        .distinct()
        .order_by("continent")
    )

    return render(request, "feed/feed.html", {
        "destinos": destinos,
        "roteiros": roteiros,
        "tab": tab,
        "continentes": continentes,
        "continente_ativo": continente,
    })


def destination_detail(request, slug):
    dest = get_object_or_404(FeaturedDestination, slug=slug, is_active=True)
    return render(request, "feed/destination_detail.html", {"dest": dest})


def public_destination_detail(request, pk):
    dest = get_object_or_404(
        Destination,
        pk=pk,
        visibility=Destination.VISIBILITY_PUBLIC,
        status=Destination.STATUS_ACTIVE,
    )
    return render(request, "feed/public_destination_detail.html", {"dest": dest})


def public_roteiro_detail(request, pk):
    roteiro = get_object_or_404(Roteiro, pk=pk, visibility=Roteiro.VISIBILITY_PUBLIC)
    dias = roteiro.dias.prefetch_related("indicacoes").all()

    user_destinations = []
    if request.user.is_authenticated:
        user_destinations = list(
            Destination.objects.filter(user=request.user, status=Destination.STATUS_ACTIVE)
            .values("pk", "name", "country")
            .order_by("name")
        )

    return render(request, "feed/public_roteiro_detail.html", {
        "roteiro": roteiro,
        "dias": dias,
        "user_destinations": user_destinations,
    })
