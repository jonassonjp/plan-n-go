"""
Plan N'Go — Testes do geocoding e autocomplete de destinos
"""

import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


# =============================================================
# Fixtures
# =============================================================

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="viajante@plango.app",
        name="Viajante Teste",
        password="senha@1234",
        is_active=True,
    )


NOMINATIM_RESPONSE = [
    {
        "place_id": 123456,
        "name": "Machu Picchu",
        "display_name": "Machu Picchu, Cusco, Peru",
        "lat": "-13.1631",
        "lon": "-72.5450",
        "address": {
            "country": "Peru",
            "country_code": "pe",
            "state": "Cusco",
        },
    }
]


# =============================================================
# Testes do Backend Nominatim
# =============================================================

class TestNominatimBackend:

    def test_autocomplete_retorna_sugestoes(self):
        from destinations.geocoding import NominatimBackend
        backend = NominatimBackend()

        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: NOMINATIM_RESPONSE,
            )
            results = backend.autocomplete("Machu Picchu")

        assert len(results) == 1
        assert results[0]["name"] == "Machu Picchu"
        assert results[0]["country"] == "Peru"
        assert results[0]["source"] == "nominatim"

    def test_autocomplete_detecta_continente(self):
        from destinations.geocoding import NominatimBackend
        backend = NominatimBackend()

        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: NOMINATIM_RESPONSE,
            )
            results = backend.autocomplete("Machu Picchu")

        assert results[0]["continent"] == "América do Sul"

    def test_autocomplete_query_curta_retorna_vazio(self):
        from destinations.geocoding import NominatimBackend
        backend = NominatimBackend()
        assert backend.autocomplete("M") == []
        assert backend.autocomplete("") == []

    def test_autocomplete_erro_de_rede_retorna_vazio(self):
        from destinations.geocoding import NominatimBackend
        import requests as req_module
        backend = NominatimBackend()

        with patch("requests.get", side_effect=req_module.RequestException):
            results = backend.autocomplete("Paris")

        assert results == []

    def test_autocomplete_deduplica_resultados(self):
        from destinations.geocoding import NominatimBackend
        backend = NominatimBackend()

        duplicated = NOMINATIM_RESPONSE * 3
        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: duplicated,
            )
            results = backend.autocomplete("Machu")

        assert len(results) == 1

    def test_mapeamento_pais_brasil(self):
        from destinations.geocoding import NominatimBackend
        backend = NominatimBackend()

        br_response = [{
            "place_id": 999,
            "name": "Chapada Diamantina",
            "display_name": "Chapada Diamantina, Bahia, Brasil",
            "lat": "-12.5",
            "lon": "-41.5",
            "address": {
                "country": "Brazil",
                "country_code": "br",
                "state": "Bahia",
            },
        }]

        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: br_response,
            )
            results = backend.autocomplete("Chapada")

        assert results[0]["country"] == "Brasil"
        assert results[0]["continent"] == "América do Sul"
        assert results[0]["country_code"] == "BR"


# =============================================================
# Testes da Factory
# =============================================================

class TestGeocodingFactory:

    def test_factory_retorna_nominatim_por_padrao(self, settings):
        from destinations.geocoding import get_geocoding_backend, NominatimBackend
        settings.GEOCODING_BACKEND = "nominatim"
        backend = get_geocoding_backend()
        assert isinstance(backend, NominatimBackend)

    def test_factory_retorna_google_quando_configurado(self, settings):
        from destinations.geocoding import get_geocoding_backend, GooglePlacesBackend
        settings.GEOCODING_BACKEND = "google"
        settings.GOOGLE_PLACES_API_KEY = "fake-key"
        backend = get_geocoding_backend()
        assert isinstance(backend, GooglePlacesBackend)

    def test_factory_padrao_sem_configuracao(self, settings):
        from destinations.geocoding import get_geocoding_backend, NominatimBackend
        if hasattr(settings, "GEOCODING_BACKEND"):
            delattr(settings, "GEOCODING_BACKEND")
        backend = get_geocoding_backend()
        assert isinstance(backend, NominatimBackend)


# =============================================================
# Testes do Endpoint de Autocomplete
# =============================================================

class TestAutocompleteView:

    def test_requer_login(self, client, db):
        response = client.get(reverse("destinations:autocomplete") + "?q=paris")
        assert response.status_code == 302

    def test_query_curta_retorna_lista_vazia(self, client, user):
        client.force_login(user)
        response = client.get(reverse("destinations:autocomplete") + "?q=p")
        assert response.status_code == 200
        data = response.json()
        assert data["suggestions"] == []

    def test_retorna_sugestoes(self, client, user):
        client.force_login(user)

        with patch("destinations.geocoding.NominatimBackend.autocomplete",
                   return_value=[{
                       "place_id": 1, "name": "Paris",
                       "label": "Paris, Île-de-France, França",
                       "country": "França", "country_code": "FR",
                       "continent": "Europa", "lat": "48.8566",
                       "lon": "2.3522", "source": "nominatim",
                   }]):
            response = client.get(
                reverse("destinations:autocomplete") + "?q=paris"
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["suggestions"]) == 1
        assert data["suggestions"][0]["name"] == "Paris"

    def test_erro_de_geocoding_retorna_lista_vazia(self, client, user):
        client.force_login(user)

        with patch("destinations.geocoding.NominatimBackend.autocomplete",
                   return_value=[]):
            response = client.get(
                reverse("destinations:autocomplete") + "?q=xyzxyzxyz"
            )

        assert response.status_code == 200
        assert response.json()["suggestions"] == []

    def test_retorna_json(self, client, user):
        client.force_login(user)

        with patch("destinations.geocoding.NominatimBackend.autocomplete",
                   return_value=[]):
            response = client.get(
                reverse("destinations:autocomplete") + "?q=tokyo"
            )

        assert response["Content-Type"] == "application/json"
