"""
Plan N'Go — Busca de imagem via Unsplash API
Gratuito: 50 buscas/hora sem billing.
"""

import requests
from django.conf import settings


def search_destination_image(destination_name: str, country: str = "") -> str:
    """
    Busca uma imagem do destino via Unsplash API.
    Retorna a URL da primeira imagem encontrada ou string vazia.
    """
    api_key = getattr(settings, "UNSPLASH_ACCESS_KEY", "")

    if not api_key:
        return ""

    query = f"{destination_name} {country} travel".strip()

    try:
        response = requests.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query":       query,
                "per_page":    1,
                "orientation": "landscape",
            },
            headers={"Authorization": f"Client-ID {api_key}"},
            timeout=8,
        )
        response.raise_for_status()
        results = response.json().get("results", [])

        if results:
            return results[0]["urls"]["regular"]

    except Exception:
        pass

    return ""
