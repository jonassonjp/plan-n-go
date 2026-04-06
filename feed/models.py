"""
Plan N'Go — Model FeaturedDestination
Destinos criados pelo superusuário, públicos para todos os visitantes.
Exibidos na landing page como cards de exemplo.
"""

from django.db import models


class FeaturedDestination(models.Model):

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
    name      = models.CharField(max_length=200, verbose_name="Nome do destino")
    country   = models.CharField(max_length=100, verbose_name="País")
    continent = models.CharField(max_length=50,  blank=True, verbose_name="Continente")
    slug      = models.SlugField(max_length=200, unique=True, verbose_name="Slug (URL)")

    # Informações práticas
    languages   = models.JSONField(default=list, blank=True, verbose_name="Idiomas")
    currency    = models.CharField(max_length=10, blank=True, verbose_name="Moeda")
    best_months = models.JSONField(default=list, blank=True, verbose_name="Melhores meses")

    # Imagem
    photo_upload = models.ImageField(
        upload_to="featured/",
        blank=True, null=True,
        verbose_name="Foto (upload)",
    )
    photo_url = models.URLField(blank=True, verbose_name="Foto (URL externa)")

    # Exigências de entrada
    visa_required = models.BooleanField(null=True, blank=True, default=None,
                                        verbose_name="Visto necessário")
    visa_type     = models.CharField(max_length=100, blank=True, verbose_name="Tipo de visto")

    vaccination_required = models.BooleanField(null=True, blank=True, default=None,
                                               verbose_name="Vacina necessária")
    vaccines       = models.JSONField(default=list, blank=True, verbose_name="Vacinas")
    vaccines_notes = models.TextField(blank=True, verbose_name="Obs. vacinas")

    other_requirements_title       = models.CharField(max_length=100, blank=True)
    other_requirements_description = models.TextField(blank=True)

    # Descrição editorial (escrita pelo superusuário)
    description = models.TextField(blank=True, verbose_name="Descrição do destino")

    # Controle
    is_active  = models.BooleanField(default=True, verbose_name="Ativo")
    order      = models.PositiveIntegerField(default=0, verbose_name="Ordem de exibição")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Destino em Destaque"
        verbose_name_plural = "Destinos em Destaque"
        ordering            = ["order", "name"]

    def __str__(self):
        return f"{self.name} — {self.country}"

    @property
    def photo(self):
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
