"""
Plan N'Go — Admin do app feed
Superusuário gerencia destinos em destaque pelo Django Admin.
"""

from django.contrib import admin
from .models import FeaturedDestination


@admin.register(FeaturedDestination)
class FeaturedDestinationAdmin(admin.ModelAdmin):
    list_display  = ["name", "country", "continent", "is_active", "order"]
    list_editable = ["is_active", "order"]
    list_filter   = ["is_active", "continent"]
    search_fields = ["name", "country"]
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        ("Identificação", {
            "fields": ("name", "slug", "country", "continent", "description"),
        }),
        ("Imagem", {
            "fields": ("photo_upload", "photo_url"),
        }),
        ("Informações práticas", {
            "fields": ("languages", "currency", "best_months"),
        }),
        ("Exigências de entrada", {
            "fields": (
                "visa_required", "visa_type",
                "vaccination_required", "vaccines", "vaccines_notes",
                "other_requirements_title", "other_requirements_description",
            ),
            "classes": ("collapse",),
        }),
        ("Controle", {
            "fields": ("is_active", "order"),
        }),
    )
