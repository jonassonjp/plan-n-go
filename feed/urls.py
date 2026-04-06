"""
Plan N'Go — URLs do app feed
"""

from django.urls import path
from . import views

app_name = "feed"

urlpatterns = [
    path("destino/<slug:slug>/", views.destination_detail, name="destination_detail"),
]
