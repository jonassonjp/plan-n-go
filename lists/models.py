"""
Plan N'Go — Models do app lists

Listas de destinos: manuais ou inteligentes (com critérios automáticos).
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import uuid

User = get_user_model()


class DestinationList(models.Model):
    """
    Lista de destinos criada pelo usuário.

    Pode ser:
    - Manual: o usuário escolhe quais destinos incluir.
    - Inteligente: filtrada por critérios (continente, país, idioma, mês).
    """

    TYPE_MANUAL = "manual"
    TYPE_SMART = "smart"
    TYPE_CHOICES = [
        (TYPE_MANUAL, "Manual"),
        (TYPE_SMART, "Inteligente"),
    ]

    VISIBILITY_PRIVATE = "private"
    VISIBILITY_RESTRICTED = "restricted"
    VISIBILITY_PUBLIC = "public"
    VISIBILITY_CHOICES = [
        (VISIBILITY_PRIVATE, "Privada"),
        (VISIBILITY_RESTRICTED, "Restrita"),
        (VISIBILITY_PUBLIC, "Pública"),
    ]

    # Identificação
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="destination_lists"
    )
    name = models.CharField(max_length=200, verbose_name="Nome da lista")
    description = models.TextField(blank=True, verbose_name="Descrição")
    emoji = models.CharField(
        max_length=8, blank=True, default="📍", verbose_name="Emoji"
    )
    slug = models.SlugField(max_length=220, blank=True)

    # Tipo de lista
    list_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_MANUAL,
        verbose_name="Tipo",
    )

    # Critérios para listas inteligentes (JSONField)
    # Formato: {"continents": [...], "countries": [...], "languages": [...], "months": [...]}
    smart_criteria = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Critérios inteligentes",
    )

    # Destinos da lista manual (ManyToMany via intermediária para preservar ordem)
    destinations = models.ManyToManyField(
        "destinations.Destination",
        through="ListItem",
        related_name="lists",
        blank=True,
    )

    # Controle
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_PRIVATE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lista de destinos"
        verbose_name_plural = "Listas de destinos"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.name} ({self.user})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or str(uuid.uuid4())[:8]
            self.slug = f"{self.user_id}-{base}"
        super().save(*args, **kwargs)

    @property
    def is_smart(self):
        return self.list_type == self.TYPE_SMART

    def get_destinations(self):
        """
        Retorna os destinos da lista.
        - Manual: via ListItem, ordenados por position.
        - Inteligente: filtrado pelos critérios do usuário.
        """
        from destinations.models import Destination

        if self.list_type == self.TYPE_MANUAL:
            return Destination.objects.filter(
                list_items__destination_list=self
            ).order_by("list_items__position")

        # Lista inteligente
        qs = Destination.objects.filter(user=self.user)
        c = self.smart_criteria or {}

        if c.get("continents"):
            qs = qs.filter(continent__in=c["continents"])
        if c.get("countries"):
            qs = qs.filter(country__in=c["countries"])
        if c.get("languages"):
            pks = [
                d.pk
                for d in qs
                if any(lang in d.languages for lang in c["languages"])
            ]
            qs = qs.filter(pk__in=pks)
        if c.get("months"):
            months = [int(m) for m in c["months"]]
            pks = [
                d.pk
                for d in qs
                if any(m in d.best_months for m in months)
            ]
            qs = qs.filter(pk__in=pks)

        return qs

    def destination_count(self):
        return self.get_destinations().count()


class ListItem(models.Model):
    """
    Intermediária entre DestinationList e Destination.
    Preserva a ordem de inserção do usuário.
    """

    destination_list = models.ForeignKey(
        DestinationList, on_delete=models.CASCADE, related_name="list_items"
    )
    destination = models.ForeignKey(
        "destinations.Destination",
        on_delete=models.CASCADE,
        related_name="list_items",
    )
    position = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Item da lista"
        verbose_name_plural = "Itens da lista"
        ordering = ["position", "added_at"]
        unique_together = [("destination_list", "destination")]

    def __str__(self):
        return f"{self.destination_list.name} → {self.destination.name}"
