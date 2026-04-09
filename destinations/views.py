"""
Plan N'Go — Views do app destinations
"""

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
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


def _get_context(extra=None):
    ctx = {"languages": LANGUAGES, "months": MONTHS, "vaccines": VACCINES}
    if extra:
        ctx.update(extra)
    return ctx


def _save_destination(request, instance=None):
    """Cria ou atualiza um destino a partir do POST."""
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

    photo_url_input = request.POST.get("photo_url", "").strip()
    photo_upload    = request.FILES.get("photo_upload")

    if not name or not country:
        return None, "Nome e país são obrigatórios."

    visa_required = None
    if visa == "true":  visa_required = True
    elif visa == "false": visa_required = False

    vaccination_required = None
    if vaccination == "true":  vaccination_required = True
    elif vaccination == "false": vaccination_required = False

    if instance is None:
        instance = Destination(user=request.user)

    instance.name        = name
    instance.country     = country
    instance.continent   = continent
    instance.currency    = currency
    instance.languages   = languages
    instance.best_months = best_months
    instance.visa_required           = visa_required
    instance.vaccination_required    = vaccination_required
    instance.vaccines                = vaccines
    instance.vaccines_notes          = vaccines_notes
    instance.other_requirements_title       = other_title
    instance.other_requirements_description = other_desc
    instance.status = Destination.STATUS_ACTIVE

    # Imagem: upload tem prioridade; se não houver upload mas URL, usa URL
    if photo_upload:
        instance.photo_upload = photo_upload
    elif photo_url_input:
        instance.photo_url = photo_url_input
    elif not instance.pk:
        # Fallback para destinos novos sem imagem
        instance.photo_url = f"https://source.unsplash.com/800x600/?{name},travel"

    instance.save()
    return instance, None


# =============================================================
# Autocomplete
# =============================================================

@login_required
@require_GET
def autocomplete_view(request):
    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return JsonResponse({"suggestions": []})
    suggestions = get_geocoding_backend().autocomplete(query)
    return JsonResponse({"suggestions": suggestions})


@login_required
@require_GET
def place_details_view(request):
    place_id = request.GET.get("place_id", "").strip()
    if not place_id:
        return JsonResponse({"error": "place_id obrigatório"}, status=400)
    details = get_geocoding_backend().place_details(place_id)
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
    return render(request, "destinations/dashboard.html",
                  _get_context({"destinations": destinations}))


# =============================================================
# Criar destino
# =============================================================

@login_required
def create(request):
    if request.method == "POST":
        instance, error = _save_destination(request)
        if error:
            messages.error(request, error)
        else:
            messages.success(request, f"{instance.name} adicionado com sucesso!")
    return redirect("destinations:dashboard")


# =============================================================
# Editar destino — retorna JSON com dados para preencher o modal
# =============================================================

@login_required
@require_GET
def edit_data(request, pk):
    """Retorna os dados do destino em JSON para preencher o modal de edição."""
    dest = get_object_or_404(request.user.destinations, pk=pk)
    return JsonResponse({
        "id":           dest.pk,
        "name":         dest.name,
        "country":      dest.country,
        "continent":    dest.continent,
        "currency":     dest.currency,
        "languages":    dest.languages,
        "best_months":  dest.best_months,
        "visa_required": "" if dest.visa_required is None
                         else ("true" if dest.visa_required else "false"),
        "vaccination_required": "" if dest.vaccination_required is None
                                else ("true" if dest.vaccination_required else "false"),
        "vaccines":      dest.vaccines,
        "vaccines_notes": dest.vaccines_notes,
        "other_requirements_title":       dest.other_requirements_title,
        "other_requirements_description": dest.other_requirements_description,
        "photo_url":    dest.photo_url,
        "photo":        dest.photo,
    })


@login_required
def update(request, pk):
    """Salva as alterações de um destino existente."""
    dest = get_object_or_404(request.user.destinations, pk=pk)
    if request.method == "POST":
        instance, error = _save_destination(request, instance=dest)
        if error:
            messages.error(request, error)
        else:
            messages.success(request, f"{instance.name} atualizado com sucesso!")
    return redirect("destinations:dashboard")


# =============================================================
# Deletar destino
# =============================================================

@login_required
def delete(request, pk):
    dest = get_object_or_404(request.user.destinations, pk=pk)
    name = dest.name
    dest.delete()
    messages.success(request, f"{name} removido.")
    return redirect("destinations:dashboard")


"""
Plan N'Go — View de importação por URL ou texto livre
Adicionar/substituir em destinations/views.py
"""


@login_required
@require_POST
def import_url_view(request):
    """
    Endpoint AJAX para importar destino por URL ou texto livre.
    POST /destinations/import-url/
    Body: { "url": "...", "text": "..." }
    """
    import json as _json
    from .importer import (import_from_url, import_from_text,
                           ScrapingError, ExtractionError)
    from django.conf import settings

    try:
        body = _json.loads(request.body)
        url  = body.get("url",  "").strip()
        text = body.get("text", "").strip()
    except Exception:
        return JsonResponse({"error": "Requisição inválida."}, status=400)

    if not url and not text:
        return JsonResponse({"error": "Informe uma URL ou cole um texto."}, status=400)

    if not getattr(settings, "ANTHROPIC_API_KEY", ""):
        return JsonResponse(
            {"error": "ANTHROPIC_API_KEY não configurada no .env."},
            status=500
        )

    try:
        if text:
            data = import_from_text(text, url)
        else:
            data = import_from_url(url)
        return JsonResponse({"success": True, "data": data})

    except ScrapingError as e:
        return JsonResponse({"error": str(e)}, status=422)
    except ExtractionError:
        return JsonResponse(
            {"error": "Não foi possível identificar o destino no conteúdo."},
            status=422
        )
    except Exception as e:
        return JsonResponse({"error": "Erro inesperado. Tente novamente."}, status=500)
# =============================================================

@login_required
@require_POST
def import_url_view(request):
    """
    Endpoint AJAX para importar destino por URL.
    POST /destinations/import-url/
    """
    import json as _json
    from .importer import import_from_url, ScrapingError, ExtractionError
    from django.conf import settings

    try:
        body = _json.loads(request.body)
        url  = body.get("url",  "").strip()
        text = body.get("text", "").strip()
    except Exception:
        return JsonResponse({"error": "Requisição inválida."}, status=400)

    if not url and not text:
        return JsonResponse({"error": "Informe uma URL ou cole um texto."}, status=400)

    if not getattr(settings, "ANTHROPIC_API_KEY", ""):
        return JsonResponse({"error": "ANTHROPIC_API_KEY não configurada no .env."}, status=500)

    try:
        from .importer import import_from_text as _import_text
        if text:
            data = _import_text(text, url)
        else:
            data = import_from_url(url)
        return JsonResponse({"success": True, "data": data})
    except ScrapingError as e:
        return JsonResponse({"error": str(e)}, status=422)
    except ExtractionError:
        return JsonResponse({"error": "Não foi possível identificar o destino."}, status=422)
    except Exception:
        return JsonResponse({"error": "Erro inesperado. Tente novamente."}, status=500)
