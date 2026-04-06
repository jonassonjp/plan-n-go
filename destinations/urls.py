"""
Plan N'Go — URLs do app destinations
"""

from django.urls import path
from . import views

app_name = "destinations"

urlpatterns = [
    path("",        views.dashboard, name="dashboard"),
    path("create/", views.create,    name="create"),
    path("<int:pk>/delete/", views.delete, name="delete"),
]
