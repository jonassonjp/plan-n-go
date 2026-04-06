"""
Plan N'Go — Model Destination
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Destination(models.Model):

    STATUS_DRAFT  = "draft"
    STATUS_ACTIVE = "active"
    STATUS_CHOICES = [
        (STATUS_DRAFT,  "Rascunho"),
        (STATUS_ACTIVE, "Ativo"),
    ]

    VISIBILITY_PRIVATE    = "private"
    VISIBILITY_RESTRICTED = "restricted"
    VISIBILITY_PUBLIC     = "public"
    VISIBILITY_CHOICES = [
        (VISIBILITY_PRIVATE,    "Privado"),
        (VISIBILITY_RESTRICTED, "Restrito"),
        (VISIBILITY_PUBLIC,     "Público"),
    ]

    VACCINE_CHOICES = [
        ("febre_amarela", "Febre Amarela"),
        ("covid",         "COVID-19"),
        ("hepatite_a",    "Hepatite A"),
        ("hepatite_b",    "Hepatite B"),
        ("tifoide",       "Febre Tifóide"),
        ("colera",        "Cólera"),
        ("meningite",     "Meningite"),
        ("raiva",         "Raiva"),
        ("encefalite",    "Encefalite Japonesa"),
        ("poliomielite",  "Poliomielite"),
        ("outra",         "Outra"),
    ]

    # Identificação
    user      = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name="destinations")
    name      = models.CharField(max_length=200, verbose_name="Nome do destino")
    country   = models.CharField(max_length=100, verbose_name="País")
    continent = models.CharField(max_length=50, blank=True, verbose_name="Continente")
    city      = models.CharField(max_length=100, blank=True, verbose_name="Cidade")

    # Informações práticas
    languages   = models.JSONField(default=list, blank=True)
    currency    = models.CharField(max_length=10, blank=True)
    best_months = models.JSONField(default=list, blank=True)

    # Imagem — upload OU url externa
    photo_upload = models.ImageField(
        upload_to="destinations/",
        blank=True,
        null=True,
        verbose_name="Foto (upload)",
    )
    photo_url = models.URLField(
        blank=True,
        verbose_name="Foto (URL externa)",
    )

    # Exigências de entrada
    visa_required   = models.BooleanField(null=True, blank=True, default=None)
    visa_type       = models.CharField(max_length=100, blank=True)

    vaccination_required = models.BooleanField(null=True, blank=True, default=None)
    vaccines        = models.JSONField(default=list, blank=True)
    vaccines_notes  = models.TextField(blank=True)

    other_requirements_title       = models.CharField(max_length=100, blank=True)
    other_requirements_description = models.TextField(blank=True)

    # Fonte (importação por URL)
    source_url         = models.URLField(blank=True)
    source_description = models.TextField(blank=True)

    # Controle
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES,
                                  default=VISIBILITY_PRIVATE)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                  default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Destino"
        verbose_name_plural = "Destinos"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.country}"

    @property
    def photo(self):
        """Retorna a URL da foto — upload tem prioridade sobre URL externa."""
        if self.photo_upload:
            return self.photo_upload.url
        if self.photo_url:
            return self.photo_url
        return None

    @property
    def best_months_display(self):
        LABELS = {1:"Jan",2:"Fev",3:"Mar",4:"Abr",5:"Mai",6:"Jun",
                  7:"Jul",8:"Ago",9:"Set",10:"Out",11:"Nov",12:"Dez"}
        if not self.best_months:
            return ""
        months = sorted(self.best_months)
        labels = [LABELS[m] for m in months[:2]]
        return ", ".join(labels) + ("+" if len(months) > 2 else "")

    @property
    def vaccine_labels(self):
        mapping = dict(self.VACCINE_CHOICES)
        return [mapping.get(v, v) for v in self.vaccines]

    @property
    def is_draft(self):
        return self.status == self.STATUS_DRAFT
