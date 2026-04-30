from django.contrib import admin
from .models import Roteiro, Dia, Indicacao


class IndicacaoInline(admin.TabularInline):
    model = Indicacao
    extra = 0


class DiaInline(admin.StackedInline):
    model = Dia
    extra = 0
    show_change_link = True


@admin.register(Roteiro)
class RoteiroAdmin(admin.ModelAdmin):
    list_display  = ("title", "destination", "user", "visibility", "num_dias", "updated_at")
    list_filter   = ("visibility",)
    search_fields = ("title", "destination__name", "user__email")
    inlines       = [DiaInline]


@admin.register(Dia)
class DiaAdmin(admin.ModelAdmin):
    list_display = ("roteiro", "numero", "titulo", "data")
    inlines      = [IndicacaoInline]


@admin.register(Indicacao)
class IndicacaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo", "dia", "horario_sugerido", "custo_estimado")
    list_filter  = ("tipo",)
