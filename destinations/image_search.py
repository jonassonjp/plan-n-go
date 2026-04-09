"""
Plan N'Go — Busca de imagem via Google Custom Search API
Usado para buscar automaticamente uma foto do destino.
"""

import requests
from django.conf import settings


def search_destination_image(destination_name: str, country: str = "") -> str:
    """
    Busca uma imagem do destino via Google Custom Search API.
    Retorna a URL da primeira imagem encontrada ou string vazia.
    """
    api_key = getattr(settings, "GOOGLE_CUSTOM_SEARCH_KEY", "")
    cx      = getattr(settings, "GOOGLE_CUSTOM_SEARCH_CX", "")

    if not api_key or not cx:
        return ""

    query = f"{destination_name} {country} travel landscape".strip()

    try:
        response = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "key":        api_key,
                "cx":         cx,
                "q":          query,
                "searchType": "image",
                "num":        1,
                "imgSize":    "LARGE",
                "imgType":    "photo",
                "safe":       "active",
            },
            timeout=8,
        )
        response.raise_for_status()
        data  = response.json()
        items = data.get("items", [])

        if items:
            return items[0].get("link", "")

    except Exception:
        pass

    return ""
