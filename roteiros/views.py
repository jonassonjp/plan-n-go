"""
Plan N'Go — Views do app roteiros
"""

import json
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse

from destinations.models import Destination
from .models import Roteiro, Dia, Indicacao

TIPOS_INDICACAO = [
    {"value": t, "label": l}
    for t, l in Indicacao.TIPO_CHOICES
]

VISIBILIDADES = [
    {"value": v, "label": l}
    for v, l in Roteiro.VISIBILITY_CHOICES
]


def _decimal_or_none(value):
    try:
        return Decimal(str(value).replace(",", "."))
    except (InvalidOperation, TypeError):
        return None


# ── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    roteiros = Roteiro.objects.filter(user=request.user).select_related("destination")
    return render(request, "roteiros/dashboard.html", {"roteiros": roteiros})


# ── Criar roteiro ─────────────────────────────────────────────────────────────

@login_required
def create(request, dest_pk):
    destination = get_object_or_404(Destination, pk=dest_pk, user=request.user)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        if not title:
            messages.error(request, "O título é obrigatório.")
            return redirect("roteiros:create", dest_pk=dest_pk)

        roteiro = Roteiro.objects.create(
            user=request.user,
            destination=destination,
            title=title,
            description=request.POST.get("description", "").strip(),
            visibility=request.POST.get("visibility", Roteiro.VISIBILITY_PRIVATE),
            custo_hospedagem=_decimal_or_none(request.POST.get("custo_hospedagem")),
            custo_alimentacao=_decimal_or_none(request.POST.get("custo_alimentacao")),
            taxa_cambio=_decimal_or_none(request.POST.get("taxa_cambio")),
        )
        messages.success(request, f"Roteiro '{roteiro.title}' criado!")
        return redirect("roteiros:detail", pk=roteiro.pk)

    return render(request, "roteiros/create.html", {
        "destination": destination,
        "visibilidades": VISIBILIDADES,
    })


# ── Detalhe ───────────────────────────────────────────────────────────────────

@login_required
def detail(request, pk):
    roteiro = get_object_or_404(Roteiro, pk=pk, user=request.user)
    dias = roteiro.dias.prefetch_related("indicacoes").all()
    return render(request, "roteiros/detail.html", {
        "roteiro": roteiro,
        "dias": dias,
        "tipos": TIPOS_INDICACAO,
        "visibilidades": VISIBILIDADES,
    })


# ── Editar roteiro ────────────────────────────────────────────────────────────

@login_required
@require_POST
def edit(request, pk):
    roteiro = get_object_or_404(Roteiro, pk=pk, user=request.user)

    title = request.POST.get("title", "").strip()
    if not title:
        messages.error(request, "O título é obrigatório.")
        return redirect("roteiros:detail", pk=pk)

    roteiro.title       = title
    roteiro.description = request.POST.get("description", "").strip()
    roteiro.visibility  = request.POST.get("visibility", roteiro.visibility)
    roteiro.custo_hospedagem  = _decimal_or_none(request.POST.get("custo_hospedagem"))
    roteiro.custo_alimentacao = _decimal_or_none(request.POST.get("custo_alimentacao"))
    roteiro.taxa_cambio       = _decimal_or_none(request.POST.get("taxa_cambio"))
    roteiro.save()

    messages.success(request, "Roteiro atualizado!")
    return redirect("roteiros:detail", pk=pk)


# ── Excluir roteiro ───────────────────────────────────────────────────────────

@login_required
@require_POST
def delete(request, pk):
    roteiro = get_object_or_404(Roteiro, pk=pk, user=request.user)
    name = roteiro.title
    roteiro.delete()
    messages.success(request, f"Roteiro '{name}' excluído.")
    return redirect("roteiros:dashboard")


# ── Copiar roteiro público ────────────────────────────────────────────────────

@login_required
@require_POST
def copy(request, pk):
    original = get_object_or_404(Roteiro, pk=pk, visibility=Roteiro.VISIBILITY_PUBLIC)

    # Destino do usuário que vai receber a cópia (informado no POST)
    dest_pk = request.POST.get("destination_id")
    destination = get_object_or_404(Destination, pk=dest_pk, user=request.user)

    novo = Roteiro.objects.create(
        user=request.user,
        destination=destination,
        title=f"{original.title} (cópia)",
        description=original.description,
        visibility=Roteiro.VISIBILITY_PRIVATE,
        custo_hospedagem=original.custo_hospedagem,
        custo_alimentacao=original.custo_alimentacao,
        taxa_cambio=original.taxa_cambio,
        copiado_de=original,
    )

    for dia in original.dias.prefetch_related("indicacoes").all():
        novo_dia = Dia.objects.create(
            roteiro=novo,
            numero=dia.numero,
            data=dia.data,
            titulo=dia.titulo,
        )
        for ind in dia.indicacoes.all():
            Indicacao.objects.create(
                dia=novo_dia,
                tipo=ind.tipo,
                nome=ind.nome,
                descricao=ind.descricao,
                horario_sugerido=ind.horario_sugerido,
                custo_estimado=ind.custo_estimado,
                ordem=ind.ordem,
            )

    messages.success(request, f"Roteiro copiado! Agora é seu para editar.")
    return redirect("roteiros:detail", pk=novo.pk)


# ── Gerar roteiro por IA ──────────────────────────────────────────────────────

@login_required
@require_POST
def generate_ai(request, pk):
    roteiro = get_object_or_404(Roteiro, pk=pk, user=request.user)

    num_dias = int(request.POST.get("num_dias", 5))
    num_dias = max(1, min(num_dias, 30))

    from django.conf import settings
    if not getattr(settings, "ANTHROPIC_API_KEY", ""):
        return JsonResponse({"error": "ANTHROPIC_API_KEY não configurada."}, status=500)

    try:
        dados = _gerar_roteiro_claude(roteiro, num_dias)
    except Exception as e:
        return JsonResponse({"error": f"Erro ao gerar roteiro: {e}"}, status=500)

    # Remove dias existentes e recria com os dados da IA
    roteiro.dias.all().delete()
    for dia_data in dados.get("dias", []):
        dia = Dia.objects.create(
            roteiro=roteiro,
            numero=dia_data["numero"],
            titulo=dia_data.get("titulo", ""),
        )
        for i, ind_data in enumerate(dia_data.get("indicacoes", [])):
            Indicacao.objects.create(
                dia=dia,
                tipo=ind_data.get("tipo", Indicacao.TIPO_TURISMO),
                nome=ind_data.get("nome", ""),
                descricao=ind_data.get("descricao", ""),
                horario_sugerido=ind_data.get("horario_sugerido") or None,
                custo_estimado=_decimal_or_none(ind_data.get("custo_estimado")),
                ordem=i,
            )

    messages.success(request, "Roteiro gerado pela IA! Revise e adapte como quiser.")
    return JsonResponse({"success": True, "redirect": f"/roteiros/{roteiro.pk}/"})


def _gerar_roteiro_claude(roteiro: Roteiro, num_dias: int) -> dict:
    from anthropic import Anthropic

    dest = roteiro.destination
    client = Anthropic()

    prompt = f"""Crie um roteiro de viagem detalhado para {dest.name}, {dest.country}.

Duração: {num_dias} dias
Idiomas locais: {", ".join(dest.languages) if dest.languages else "não informado"}
Moeda local: {dest.currency or "não informada"}

Retorne APENAS um JSON válido com esta estrutura:
{{
  "dias": [
    {{
      "numero": 1,
      "titulo": "Título temático do dia",
      "indicacoes": [
        {{
          "tipo": "turismo|atividade|restaurante|cafe|mercado|outro",
          "nome": "Nome do local",
          "descricao": "Breve descrição (máx 200 chars)",
          "horario_sugerido": "09:00",
          "custo_estimado": 50.00
        }}
      ]
    }}
  ]
}}

Tipos válidos: turismo, atividade, restaurante, cafe, mercado, outro.
Inclua ao menos uma indicação de alimentação (restaurante ou café) por dia.
Horários no formato HH:MM. Custos em {dest.currency or "moeda local"}, numérico."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system="Você é um especialista em viagens. Responda APENAS com JSON válido, sem texto antes ou depois.",
        messages=[{"role": "user", "content": prompt}],
    )

    import re
    raw = message.content[0].text
    raw = re.sub(r"^```json\s*", "", raw.strip())
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


# ── Dias ─────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def dia_add(request, pk):
    roteiro = get_object_or_404(Roteiro, pk=pk, user=request.user)

    ultimo = roteiro.dias.order_by("-numero").first()
    numero = (ultimo.numero + 1) if ultimo else 1

    Dia.objects.create(
        roteiro=roteiro,
        numero=numero,
        titulo=request.POST.get("titulo", "").strip(),
    )
    messages.success(request, f"Dia {numero} adicionado.")
    return redirect("roteiros:detail", pk=pk)


@login_required
@require_POST
def dia_edit(request, pk, dia_pk):
    roteiro = get_object_or_404(Roteiro, pk=pk, user=request.user)
    dia = get_object_or_404(Dia, pk=dia_pk, roteiro=roteiro)

    dia.titulo = request.POST.get("titulo", "").strip()
    dia.data   = request.POST.get("data") or None
    dia.save()
    return redirect("roteiros:detail", pk=pk)


@login_required
@require_POST
def dia_delete(request, pk, dia_pk):
    roteiro = get_object_or_404(Roteiro, pk=pk, user=request.user)
    dia = get_object_or_404(Dia, pk=dia_pk, roteiro=roteiro)
    dia.delete()
    # Renumera os dias restantes
    for i, d in enumerate(roteiro.dias.order_by("numero"), start=1):
        if d.numero != i:
            d.numero = i
            d.save()
    messages.success(request, "Dia removido.")
    return redirect("roteiros:detail", pk=pk)


# ── Indicações ────────────────────────────────────────────────────────────────

@login_required
@require_POST
def indicacao_add(request, pk, dia_pk):
    roteiro = get_object_or_404(Roteiro, pk=pk, user=request.user)
    dia = get_object_or_404(Dia, pk=dia_pk, roteiro=roteiro)

    nome = request.POST.get("nome", "").strip()
    if not nome:
        messages.error(request, "O nome da indicação é obrigatório.")
        return redirect("roteiros:detail", pk=pk)

    ultima = dia.indicacoes.order_by("-ordem").first()
    ordem = (ultima.ordem + 1) if ultima else 0

    Indicacao.objects.create(
        dia=dia,
        tipo=request.POST.get("tipo", Indicacao.TIPO_TURISMO),
        nome=nome,
        descricao=request.POST.get("descricao", "").strip(),
        horario_sugerido=request.POST.get("horario_sugerido") or None,
        custo_estimado=_decimal_or_none(request.POST.get("custo_estimado")),
        ordem=ordem,
    )
    messages.success(request, f"'{nome}' adicionado ao Dia {dia.numero}.")
    return redirect("roteiros:detail", pk=pk)


@login_required
@require_POST
def indicacao_edit(request, pk, ind_pk):
    roteiro = get_object_or_404(Roteiro, pk=pk, user=request.user)
    indicacao = get_object_or_404(Indicacao, pk=ind_pk, dia__roteiro=roteiro)

    nome = request.POST.get("nome", "").strip()
    if not nome:
        messages.error(request, "O nome da indicação é obrigatório.")
        return redirect("roteiros:detail", pk=pk)

    indicacao.tipo            = request.POST.get("tipo", indicacao.tipo)
    indicacao.nome            = nome
    indicacao.descricao       = request.POST.get("descricao", "").strip()
    indicacao.horario_sugerido = request.POST.get("horario_sugerido") or None
    indicacao.custo_estimado  = _decimal_or_none(request.POST.get("custo_estimado"))
    indicacao.save()
    return redirect("roteiros:detail", pk=pk)


@login_required
@require_POST
def indicacao_delete(request, pk, ind_pk):
    roteiro = get_object_or_404(Roteiro, pk=pk, user=request.user)
    indicacao = get_object_or_404(Indicacao, pk=ind_pk, dia__roteiro=roteiro)
    indicacao.delete()
    return redirect("roteiros:detail", pk=pk)
