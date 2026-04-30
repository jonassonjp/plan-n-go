"""
Plan N'Go — URLs do app roteiros
"""
from django.urls import path
from . import views

app_name = "roteiros"

urlpatterns = [
    path("",                        views.dashboard,       name="dashboard"),
    path("novo/<int:dest_pk>/",     views.create,          name="create"),
    path("<int:pk>/",               views.detail,          name="detail"),
    path("<int:pk>/editar/",        views.edit,            name="edit"),
    path("<int:pk>/excluir/",       views.delete,          name="delete"),
    path("<int:pk>/copiar/",        views.copy,            name="copy"),
    path("<int:pk>/gerar-ia/",      views.generate_ai,     name="generate_ai"),

    # Dias
    path("<int:pk>/dias/adicionar/",         views.dia_add,    name="dia_add"),
    path("<int:pk>/dias/<int:dia_pk>/editar/", views.dia_edit, name="dia_edit"),
    path("<int:pk>/dias/<int:dia_pk>/excluir/", views.dia_delete, name="dia_delete"),

    # Indicações
    path("<int:pk>/dias/<int:dia_pk>/indicacoes/adicionar/",  views.indicacao_add,    name="indicacao_add"),
    path("<int:pk>/indicacoes/<int:ind_pk>/editar/",          views.indicacao_edit,   name="indicacao_edit"),
    path("<int:pk>/indicacoes/<int:ind_pk>/excluir/",         views.indicacao_delete, name="indicacao_delete"),
]
