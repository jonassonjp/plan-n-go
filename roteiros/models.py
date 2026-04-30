"""
Plan N'Go — Models do app roteiros

Roteiro → Dia → Indicacao
"""

from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Roteiro(models.Model):

    VISIBILITY_PRIVATE    = "private"
    VISIBILITY_RESTRICTED = "restricted"
    VISIBILITY_PUBLIC     = "public"
    VISIBILITY_CHOICES = [
        (VISIBILITY_PRIVATE,    "Privado"),
        (VISIBILITY_RESTRICTED, "Restrito"),
        (VISIBILITY_PUBLIC,     "Público"),
    ]

    # Identificação
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roteiros")
    destination = models.ForeignKey(
        "destinations.Destination",
        on_delete=models.CASCADE,
        related_name="roteiros",
    )
    title       = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descrição")
    visibility  = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_PRIVATE,
    )

    # Custos totais (em moeda local do destino)
    custo_hospedagem  = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        verbose_name="Custo total de hospedagem (moeda local)",
    )
    custo_alimentacao = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        verbose_name="Custo total de alimentação (moeda local)",
    )

    # Câmbio do dia (1 unidade da moeda local = ? BRL)
    taxa_cambio = models.DecimalField(
        max_digits=10, decimal_places=4,
        null=True, blank=True,
        verbose_name="Taxa de câmbio (moeda local → BRL)",
        help_text="Ex: se 1 USD = 5,20 BRL, informe 5.20",
    )

    # Cópia de roteiro público
    copiado_de = models.ForeignKey(
        "self",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="copias",
        verbose_name="Copiado de",
    )

    # Controle
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Roteiro"
        verbose_name_plural = "Roteiros"
        ordering            = ["-updated_at"]

    def __str__(self):
        return f"{self.title} — {self.destination.name}"

    # ── Propriedades de custo ──────────────────────────────────────────

    @property
    def custo_hospedagem_brl(self):
        if self.custo_hospedagem and self.taxa_cambio:
            return (self.custo_hospedagem * self.taxa_cambio).quantize(Decimal("0.01"))
        return None

    @property
    def custo_alimentacao_brl(self):
        if self.custo_alimentacao and self.taxa_cambio:
            return (self.custo_alimentacao * self.taxa_cambio).quantize(Decimal("0.01"))
        return None

    @property
    def custo_total_local(self):
        total = Decimal("0")
        if self.custo_hospedagem:
            total += self.custo_hospedagem
        if self.custo_alimentacao:
            total += self.custo_alimentacao
        return total if total else None

    @property
    def custo_total_brl(self):
        if self.custo_total_local and self.taxa_cambio:
            return (self.custo_total_local * self.taxa_cambio).quantize(Decimal("0.01"))
        return None

    @property
    def moeda(self):
        return self.destination.currency or "—"

    @property
    def num_dias(self):
        return self.dias.count()


class Dia(models.Model):

    roteiro = models.ForeignKey(Roteiro, on_delete=models.CASCADE, related_name="dias")
    numero  = models.PositiveIntegerField(verbose_name="Dia")
    data    = models.DateField(null=True, blank=True, verbose_name="Data")
    titulo  = models.CharField(max_length=200, blank=True, verbose_name="Título do dia")

    class Meta:
        verbose_name        = "Dia"
        verbose_name_plural = "Dias"
        ordering            = ["numero"]
        unique_together     = [("roteiro", "numero")]

    def __str__(self):
        label = f"Dia {self.numero}"
        if self.titulo:
            label += f" — {self.titulo}"
        return label


class Indicacao(models.Model):

    TIPO_TURISMO    = "turismo"
    TIPO_ATIVIDADE  = "atividade"
    TIPO_RESTAURANTE = "restaurante"
    TIPO_CAFE       = "cafe"
    TIPO_MERCADO    = "mercado"
    TIPO_OUTRO      = "outro"

    TIPO_CHOICES = [
        (TIPO_TURISMO,     "Ponto Turístico"),
        (TIPO_ATIVIDADE,   "Atividade"),
        (TIPO_RESTAURANTE, "Restaurante"),
        (TIPO_CAFE,        "Café"),
        (TIPO_MERCADO,     "Mercado"),
        (TIPO_OUTRO,       "Outro"),
    ]

    TIPO_ALIMENTACAO = {TIPO_RESTAURANTE, TIPO_CAFE, TIPO_MERCADO}

    dia             = models.ForeignKey(Dia, on_delete=models.CASCADE, related_name="indicacoes")
    tipo            = models.CharField(max_length=20, choices=TIPO_CHOICES, default=TIPO_TURISMO)
    nome            = models.CharField(max_length=200, verbose_name="Nome")
    descricao       = models.TextField(blank=True, verbose_name="Descrição")
    horario_sugerido = models.TimeField(null=True, blank=True, verbose_name="Horário sugerido")
    custo_estimado  = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        verbose_name="Custo estimado (moeda local)",
    )
    ordem           = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name        = "Indicação"
        verbose_name_plural = "Indicações"
        ordering            = ["ordem", "horario_sugerido"]

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.nome}"

    @property
    def is_alimentacao(self):
        return self.tipo in self.TIPO_ALIMENTACAO
