"""
Plan N'Go — URLs do app destinations
"""

from django.urls import path
from . import views

app_name = "destinations"

urlpatterns = [
    path("",                      views.dashboard,        name="dashboard"),
    path("create/",               views.create,           name="create"),
    path("<int:pk>/edit-data/",   views.edit_data,        name="edit_data"),
    path("<int:pk>/update/",      views.update,           name="update"),
    path("<int:pk>/delete/",      views.delete,           name="delete"),
    path("import-url/",        views.import_url_view, name="import_url"),
    path("autocomplete/",         views.autocomplete_view,   name="autocomplete"),
    path("place-details/",        views.place_details_view,  name="place_details"),
]
