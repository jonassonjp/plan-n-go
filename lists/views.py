"""
Plan N'Go — Views do app lists
"""

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.db import IntegrityError

from .models import DestinationList, ListItem
from destinations.models import Destination

CONTINENTS = [
    "África", "América do Norte", "América do Sul",
    "Ásia", "Europa", "Oceania", "Antártida",
]

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

EMOJIS = ["📍", "🌍", "🌎", "🌏", "✈️", "🏖️", "🏔️", "🏙️", "🗺️",
          "❤️", "⭐", "🔖", "🎯", "🌟", "🧳", "🏝️", "🗼", "🎒"]


def _base_context():
    return {
        "continents": CONTINENTS,
        "languages": LANGUAGES,
        "months": MONTHS,
        "emojis": EMOJIS,
    }


# ── Dashboard de listas ──────────────────────────────────────────────────────

@login_required
def lists_dashboard(request):
    """Página principal: lista todas as listas do usuário."""
    user_lists = DestinationList.objects.filter(user=request.user)

    # Adiciona contagem de destinos para cada lista
    lists_with_count = []
    for lst in user_lists:
        lists_with_count.append({
            "list": lst,
            "count": lst.destination_count(),
            "preview": lst.get_destinations()[:3],
        })

    ctx = _base_context()
    ctx["lists_with_count"] = lists_with_count
    return render(request, "lists/dashboard.html", ctx)


# ── Detalhe de lista ─────────────────────────────────────────────────────────

@login_required
def list_detail(request, pk):
    """Página de detalhes de uma lista, com seus destinos."""
    lst = get_object_or_404(DestinationList, pk=pk, user=request.user)
    destinations = lst.get_destinations()

    # Destinos do usuário que ainda não estão na lista (para adicionar)
    if lst.list_type == DestinationList.TYPE_MANUAL:
        in_list_pks = set(destinations.values_list("pk", flat=True))
        available = Destination.objects.filter(user=request.user).exclude(
            pk__in=in_list_pks
        )
    else:
        available = Destination.objects.none()

    ctx = _base_context()
    ctx.update({
        "lst": lst,
        "destinations": destinations,
        "available": available,
        "dest_count": destinations.count(),
    })
    return render(request, "lists/detail.html", ctx)


# ── Criar lista ──────────────────────────────────────────────────────────────

@login_required
@require_POST
def list_create(request):
    """Cria uma nova lista (manual ou inteligente)."""
    name = request.POST.get("name", "").strip()
    if not name:
        messages.error(request, "O nome da lista é obrigatório.")
        return redirect("lists:dashboard")

    list_type = request.POST.get("list_type", DestinationList.TYPE_MANUAL)
    emoji = request.POST.get("emoji", "📍")
    description = request.POST.get("description", "").strip()

    lst = DestinationList(
        user=request.user,
        name=name,
        emoji=emoji,
        description=description,
        list_type=list_type,
    )

    if list_type == DestinationList.TYPE_SMART:
        criteria = {
            "continents": request.POST.getlist("criteria_continents"),
            "countries":  [
                c.strip() for c in request.POST.get("criteria_countries", "").split(",")
                if c.strip()
            ],
            "languages":  request.POST.getlist("criteria_languages"),
            "months":     [int(m) for m in request.POST.getlist("criteria_months")],
        }
        # Remove critérios vazios
        lst.smart_criteria = {k: v for k, v in criteria.items() if v}

    lst.save()
    messages.success(request, f"Lista '{lst.name}' criada com sucesso!")
    return redirect("lists:detail", pk=lst.pk)


# ── Editar lista ─────────────────────────────────────────────────────────────

@login_required
@require_POST
def list_edit(request, pk):
    """Atualiza nome, emoji, descrição e critérios de uma lista."""
    lst = get_object_or_404(DestinationList, pk=pk, user=request.user)

    name = request.POST.get("name", "").strip()
    if not name:
        messages.error(request, "O nome da lista é obrigatório.")
        return redirect("lists:detail", pk=pk)

    lst.name = name
    lst.emoji = request.POST.get("emoji", lst.emoji)
    lst.description = request.POST.get("description", "").strip()

    if lst.list_type == DestinationList.TYPE_SMART:
        criteria = {
            "continents": request.POST.getlist("criteria_continents"),
            "countries":  [
                c.strip() for c in request.POST.get("criteria_countries", "").split(",")
                if c.strip()
            ],
            "languages":  request.POST.getlist("criteria_languages"),
            "months":     [int(m) for m in request.POST.getlist("criteria_months")],
        }
        lst.smart_criteria = {k: v for k, v in criteria.items() if v}

    lst.slug = ""  # força regeneração se o nome mudou
    lst.save()
    messages.success(request, "Lista atualizada!")
    return redirect("lists:detail", pk=lst.pk)


# ── Excluir lista ────────────────────────────────────────────────────────────

@login_required
@require_POST
def list_delete(request, pk):
    """Exclui uma lista."""
    lst = get_object_or_404(DestinationList, pk=pk, user=request.user)
    name = lst.name
    lst.delete()
    messages.success(request, f"Lista '{name}' excluída.")
    return redirect("lists:dashboard")


# ── Adicionar destino à lista (manual) ───────────────────────────────────────

@login_required
@require_POST
def list_add_destination(request, pk):
    """Adiciona um destino a uma lista manual."""
    lst = get_object_or_404(
        DestinationList, pk=pk, user=request.user,
        list_type=DestinationList.TYPE_MANUAL
    )
    dest_pk = request.POST.get("destination_id")
    dest = get_object_or_404(Destination, pk=dest_pk, user=request.user)

    # Posição = último item + 1
    last = lst.list_items.order_by("-position").first()
    position = (last.position + 1) if last else 0

    try:
        ListItem.objects.create(
            destination_list=lst,
            destination=dest,
            position=position,
        )
        messages.success(request, f"{dest.name} adicionado à lista!")
    except IntegrityError:
        messages.warning(request, f"{dest.name} já está nesta lista.")

    return redirect("lists:detail", pk=lst.pk)


# ── Remover destino da lista (manual) ────────────────────────────────────────

@login_required
@require_POST
def list_remove_destination(request, pk, dest_pk):
    """Remove um destino de uma lista manual."""
    lst = get_object_or_404(
        DestinationList, pk=pk, user=request.user,
        list_type=DestinationList.TYPE_MANUAL
    )
    dest = get_object_or_404(Destination, pk=dest_pk, user=request.user)
    ListItem.objects.filter(destination_list=lst, destination=dest).delete()
    messages.success(request, f"{dest.name} removido da lista.")
    return redirect("lists:detail", pk=lst.pk)


# ── API: listas disponíveis para um destino ──────────────────────────────────

@login_required
@require_GET
def api_lists_for_destination(request, dest_pk):
    """
    Retorna as listas manuais do usuário, indicando se o destino já está em cada uma.
    Usado pelo modal no dashboard de destinos.
    """
    dest = get_object_or_404(Destination, pk=dest_pk, user=request.user)
    manual_lists = DestinationList.objects.filter(
        user=request.user, list_type=DestinationList.TYPE_MANUAL
    )

    data = [
        {
            "id": lst.pk,
            "name": lst.name,
            "emoji": lst.emoji,
            "has_destination": lst.list_items.filter(destination=dest).exists(),
        }
        for lst in manual_lists
    ]
    return JsonResponse({"lists": data})


# ── API: toggle destino numa lista (AJAX) ────────────────────────────────────

@login_required
@require_POST
def api_toggle_destination(request, pk):
    """
    Adiciona ou remove um destino de uma lista manual via AJAX.
    Body JSON: {"destination_id": <int>}
    """
    lst = get_object_or_404(
        DestinationList, pk=pk, user=request.user,
        list_type=DestinationList.TYPE_MANUAL
    )
    try:
        body = json.loads(request.body)
        dest_pk = int(body.get("destination_id", 0))
    except (ValueError, KeyError):
        return JsonResponse({"error": "destination_id inválido"}, status=400)

    dest = get_object_or_404(Destination, pk=dest_pk, user=request.user)
    item = lst.list_items.filter(destination=dest).first()

    if item:
        item.delete()
        return JsonResponse({"action": "removed", "destination_id": dest_pk})
    else:
        last = lst.list_items.order_by("-position").first()
        position = (last.position + 1) if last else 0
        ListItem.objects.create(destination_list=lst, destination=dest, position=position)
        return JsonResponse({"action": "added", "destination_id": dest_pk})
