"""
Plan N'Go — Views do app destinations
"""

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib import messages

from .geocoding import get_geocoding_backend


# =============================================================
# Autocomplete de destinos
# =============================================================

@login_required
@require_GET
def autocomplete_view(request):
    """
    Endpoint AJAX para autocomplete de destinos.
    GET /destinations/autocomplete/?q=machu
    Retorna JSON com lista de sugestões.
    """
    query = request.GET.get("q", "").strip()

    if len(query) < 2:
        return JsonResponse({"suggestions": []})

    backend     = get_geocoding_backend()
    suggestions = backend.autocomplete(query)

    return JsonResponse({"suggestions": suggestions})


@login_required
@require_GET
def place_details_view(request):
    """
    Endpoint AJAX para buscar detalhes de um lugar selecionado.
    GET /destinations/place-details/?place_id=123456
    Retorna JSON com nome, país, continente, coordenadas.
    """
    place_id = request.GET.get("place_id", "").strip()

    if not place_id:
        return JsonResponse({"error": "place_id obrigatório"}, status=400)

    backend = get_geocoding_backend()
    details = backend.place_details(place_id)

    if not details:
        return JsonResponse({"error": "Lugar não encontrado"}, status=404)

    return JsonResponse(details)


# =============================================================
# Dashboard
# =============================================================

@login_required
def dashboard(request):
    destinations = request.user.destinations.filter(
        status="active"
    ).order_by("-created_at")

    return render(request, "destinations/dashboard.html", {
        "destinations": destinations,
    })


# =============================================================
# Criar destino
# =============================================================

@login_required
def create(request):
    if request.method == "POST":
        from .models import Destination

        name        = request.POST.get("name", "").strip()
        country     = request.POST.get("country", "").strip()
        continent   = request.POST.get("continent", "").strip()
        currency    = request.POST.get("currency", "").strip().upper()
        visa        = request.POST.get("visa_required", "")
        languages   = request.POST.getlist("languages")
        best_months = [int(m) for m in request.POST.getlist("best_months") if m.isdigit()]
        lat         = request.POST.get("lat", "").strip()
        lon         = request.POST.get("lon", "").strip()

        # Vacinas
        vaccination = request.POST.get("vaccination_required", "")
        vaccines    = request.POST.getlist("vaccines")
        vaccines_notes = request.POST.get("vaccines_notes", "").strip()

        # Outras exigências
        other_title = request.POST.get("other_requirements_title", "").strip()
        other_desc  = request.POST.get("other_requirements_description", "").strip()

        if not name or not country:
            messages.error(request, "Nome e país são obrigatórios.")
            return redirect("destinations:dashboard")

        visa_required = None
        if visa == "true":
            visa_required = True
        elif visa == "false":
            visa_required = False

        vaccination_required = None
        if vaccination == "true":
            vaccination_required = True
        elif vaccination == "false":
            vaccination_required = False

        Destination.objects.create(
            user=request.user,
            name=name,
            country=country,
            continent=continent,
            currency=currency,
            languages=languages,
            best_months=best_months,
            visa_required=visa_required,
            vaccination_required=vaccination_required,
            vaccines=vaccines,
            vaccines_notes=vaccines_notes,
            other_requirements_title=other_title,
            other_requirements_description=other_desc,
            photo_url=f"https://source.unsplash.com/800x600/?{name},travel",
            status=Destination.STATUS_ACTIVE,
        )

        messages.success(request, f"{name} adicionado com sucesso!")

    return redirect("destinations:dashboard")


# =============================================================
# Deletar destino
# =============================================================

@login_required
def delete(request, pk):
    destination = get_object_or_404(
        request.user.destinations, pk=pk
    )
    destination.delete()
    messages.success(request, f"{destination.name} removido.")
    return redirect("destinations:dashboard")
