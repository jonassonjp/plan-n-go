"""
Plan N'Go — URLs do app destinations
"""

from django.urls import path
from . import views

app_name = "destinations"

urlpatterns = [
    path("",                  views.dashboard,        name="dashboard"),
    path("create/",           views.create,           name="create"),
    path("<int:pk>/delete/",  views.delete,           name="delete"),

    # Endpoints AJAX de geocoding
    path("autocomplete/",     views.autocomplete_view,   name="autocomplete"),
    path("place-details/",    views.place_details_view,  name="place_details"),
]
