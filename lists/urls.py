"""
Plan N'Go — URLs do app lists
"""
from django.urls import path
from . import views

app_name = "lists"

urlpatterns = [
    # Dashboard de listas
    path("", views.lists_dashboard, name="dashboard"),

    # CRUD de listas
    path("nova/", views.list_create, name="create"),
    path("<int:pk>/", views.list_detail, name="detail"),
    path("<int:pk>/editar/", views.list_edit, name="edit"),
    path("<int:pk>/excluir/", views.list_delete, name="delete"),

    # Gerenciar destinos numa lista manual
    path("<int:pk>/adicionar/", views.list_add_destination, name="add_destination"),
    path("<int:pk>/remover/<int:dest_pk>/", views.list_remove_destination, name="remove_destination"),

    # API (JSON)
    path("api/destino/<int:dest_pk>/listas/", views.api_lists_for_destination, name="api_lists_for_destination"),
    path("api/<int:pk>/toggle/", views.api_toggle_destination, name="api_toggle"),
]
