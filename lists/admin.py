"""
Plan N'Go — Admin do app lists
"""
from django.contrib import admin
from .models import DestinationList, ListItem


class ListItemInline(admin.TabularInline):
    model = ListItem
    extra = 0
    readonly_fields = ("added_at",)
    fields = ("destination", "position", "added_at")
    ordering = ("position",)


@admin.register(DestinationList)
class DestinationListAdmin(admin.ModelAdmin):
    list_display = ("name", "emoji", "user", "list_type", "destination_count", "updated_at")
    list_filter = ("list_type", "visibility")
    search_fields = ("name", "user__email")
    readonly_fields = ("slug", "created_at", "updated_at")
    inlines = [ListItemInline]

    def destination_count(self, obj):
        return obj.destination_count()
    destination_count.short_description = "Destinos"


@admin.register(ListItem)
class ListItemAdmin(admin.ModelAdmin):
    list_display = ("destination_list", "destination", "position", "added_at")
    list_filter = ("destination_list",)
    search_fields = ("destination__name", "destination_list__name")
