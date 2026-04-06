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

LANGUAGES = [
    "Português", "Inglês", "Espanhol", "Francês", "Alemão",
    "Italiano", "Japonês", "Mandarim", "Coreano", "Árabe",
    "Hindi", "Russo", "Grego", "Holandês", "Sueco",
    "Tailandês", "Vietnamita", "Indonésio",
]

MONTHS = [
    {"value": 1,  "label": "Jan", "full": "Janeiro"},
    {"value": 2,  "label": "Fev", "full": "Fevereiro"},
    {"value": 3,  "label": "Mar", "full": "Março"},
    {"value": 4,  "label": "Abr", "full": "Abril"},
    {"value": 5,  "label": "Mai", "full": "Maio"},
    {"value": 6,  "label": "Jun", "full": "Junho"},
    {"value": 7,  "label": "Jul", "full": "Julho"},
    {"value": 8,  "label": "Ago", "full": "Agosto"},
    {"value": 9,  "label": "Set", "full": "Setembro"},
    {"value": 10, "label": "Out", "full": "Outubro"},
    {"value": 11, "label": "Nov", "full": "Novembro"},
    {"value": 12, "label": "Dez", "full": "Dezembro"},
]

VACCINES = [
    {"value": "febre_amarela", "label": "Febre Amarela"},
    {"value": "covid",         "label": "COVID-19"},
    {"value": "hepatite_a",    "label": "Hepatite A"},
    {"value": "hepatite_b",    "label": "Hepatite B"},
    {"value": "tifoide",       "label": "Febre Tifóide"},
    {"value": "colera",        "label": "Cólera"},
    {"value": "meningite",     "label": "Meningite"},
    {"value": "raiva",         "label": "Raiva"},
    {"value": "encefalite",    "label": "Encefalite Japonesa"},
    {"value": "poliomielite",  "label": "Poliomielite"},
    {"value": "outra",         "label": "Outra"},
]


# =============================================================
# Autocomplete
# =============================================================

@login_required
@require_GET
def autocomplete_view(request):
    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return JsonResponse({"suggestions": []})
    backend     = get_geocoding_backend()
    suggestions = backend.autocomplete(query)
    return JsonResponse({"suggestions": suggestions})


@login_required
@require_GET
def place_details_view(request):
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
        "destinations":    destinations,
        "languages":       LANGUAGES,
        "months":          MONTHS,
        "vaccines":        VACCINES,
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

        vaccination    = request.POST.get("vaccination_required", "")
        vaccines       = request.POST.getlist("vaccines")
        vaccines_notes = request.POST.get("vaccines_notes", "").strip()
        other_title    = request.POST.get("other_requirements_title", "").strip()
        other_desc     = request.POST.get("other_requirements_description", "").strip()

        if not name or not country:
            messages.error(request, "Nome e país são obrigatórios.")
            return redirect("destinations:dashboard")

        visa_required = None
        if visa == "true":  visa_required = True
        elif visa == "false": visa_required = False

        vaccination_required = None
        if vaccination == "true":  vaccination_required = True
        elif vaccination == "false": vaccination_required = False

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
    destination = get_object_or_404(request.user.destinations, pk=pk)
    name = destination.name
    destination.delete()
    messages.success(request, f"{name} removido.")
    return redirect("destinations:dashboard")
