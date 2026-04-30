"""
Plan N'Go — URLs do app feed
"""

from django.urls import path
from . import views

app_name = "feed"

urlpatterns = [
    path("", views.feed_view, name="feed"),
    path("destino/<slug:slug>/", views.destination_detail, name="destination_detail"),
    path("catalogo/<int:pk>/", views.public_destination_detail, name="public_destination_detail"),
    path("roteiro/<int:pk>/", views.public_roteiro_detail, name="public_roteiro_detail"),
]
