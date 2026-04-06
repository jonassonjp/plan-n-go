"""
Plan N'Go — Model Destination
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Destination(models.Model):

    # =========================================================
    # Status
    # =========================================================
    STATUS_DRAFT     = "draft"
    STATUS_ACTIVE    = "active"

    STATUS_CHOICES = [
        (STATUS_DRAFT,  "Rascunho"),   # importado por URL, aguarda revisão
        (STATUS_ACTIVE, "Ativo"),      # cadastrado/confirmado pelo usuário
    ]

    # =========================================================
    # Campos de identificação
    # =========================================================
    user      = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="destinations",
        verbose_name="Usuário",
    )
    name      = models.CharField(max_length=200, verbose_name="Nome do destino")
    country   = models.CharField(max_length=100, verbose_name="País")
    continent = models.CharField(max_length=50,  blank=True, verbose_name="Continente")
    city      = models.CharField(max_length=100, blank=True, verbose_name="Cidade")

    # =========================================================
    # Idiomas (lista separada por vírgula)
    # =========================================================
    languages = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Idiomas falados",
        help_text="Lista de idiomas falados no destino.",
    )

    # =========================================================
    # Informações práticas
    # =========================================================
    currency    = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Moeda",
        help_text="Ex: BRL, USD, EUR",
    )
    best_months = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Melhores meses para visitar",
        help_text="Lista de inteiros de 1 a 12.",
    )

    # =========================================================
    # Exigências de entrada
    # =========================================================

    # --- Visto ---
    visa_required = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        verbose_name="Visto necessário",
    )
    visa_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Tipo de visto",
        help_text="Ex: Visto de turismo, E-visa, Visto on arrival.",
    )

    # --- Vacinas ---
    VACCINE_CHOICES = [
        ("febre_amarela",   "Febre Amarela"),
        ("covid",           "COVID-19"),
        ("hepatite_a",      "Hepatite A"),
        ("hepatite_b",      "Hepatite B"),
        ("tifoide",         "Febre Tifóide"),
        ("colera",          "Cólera"),
        ("meningite",       "Meningite"),
        ("raiva",           "Raiva"),
        ("encefalite",      "Encefalite Japonesa"),
        ("poliomielite",    "Poliomielite"),
        ("outra",           "Outra"),
    ]

    vaccination_required = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        verbose_name="Vacina necessária",
    )
    vaccines = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Vacinas necessárias",
        help_text="Lista de códigos de vacinas obrigatórias.",
    )
    vaccines_notes = models.TextField(
        blank=True,
        verbose_name="Observações sobre vacinas",
        help_text="Detalhes sobre as vacinas ou vacinas não listadas.",
    )

    # --- Outras exigências (ex: ETIAS) ---
    other_requirements_title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Título da exigência",
        help_text="Ex: ETIAS, eTA, Registro de saúde.",
    )
    other_requirements_description = models.TextField(
        blank=True,
        verbose_name="Descrição da exigência",
        help_text="Ex: Autorização de viagem obrigatória para entrada na Europa.",
    )

    # =========================================================
    # Foto e fonte
    # =========================================================
    photo_url          = models.URLField(blank=True, verbose_name="URL da foto")
    source_url         = models.URLField(blank=True, verbose_name="URL de origem")
    source_description = models.TextField(
        blank=True,
        verbose_name="Descrição da fonte",
        help_text="Texto extraído da URL de origem (Instagram, blog, etc.).",
    )

    # =========================================================
    # Visibilidade
    # =========================================================
    VISIBILITY_PRIVATE    = "private"
    VISIBILITY_RESTRICTED = "restricted"
    VISIBILITY_PUBLIC     = "public"

    VISIBILITY_CHOICES = [
        (VISIBILITY_PRIVATE,    "Privado"),
        (VISIBILITY_RESTRICTED, "Restrito (usuários do app)"),
        (VISIBILITY_PUBLIC,     "Público"),
    ]

    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_PRIVATE,
        verbose_name="Visibilidade",
    )

    # =========================================================
    # Status e controle
    # =========================================================
    status     = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name="Status",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Destino"
        verbose_name_plural = "Destinos"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.country}"

    # =========================================================
    # Helpers
    # =========================================================
    @property
    def best_months_display(self):
        """Retorna os meses formatados. Ex: 'Jan, Fev+'"""
        MONTH_LABELS = {
            1: "Jan", 2: "Fev",  3: "Mar", 4: "Abr",
            5: "Mai", 6: "Jun",  7: "Jul", 8: "Ago",
            9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
        }
        if not self.best_months:
            return ""
        sorted_months = sorted(self.best_months)
        labels = [MONTH_LABELS[m] for m in sorted_months[:2]]
        suffix = "+" if len(sorted_months) > 2 else ""
        return ", ".join(labels) + suffix

    @property
    def vaccine_labels(self):
        """Retorna os rótulos legíveis das vacinas selecionadas."""
        mapping = dict(self.VACCINE_CHOICES)
        return [mapping.get(v, v) for v in self.vaccines]

    @property
    def is_draft(self):
        return self.status == self.STATUS_DRAFT
