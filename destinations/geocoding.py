"""
Plan N'Go — Serviço de Geocoding
Suporta dois backends: Nominatim (padrão, gratuito) e Google Places API.

Para alternar, defina no .env:
  GEOCODING_BACKEND=nominatim   # padrão, gratuito
  GEOCODING_BACKEND=google      # requer GOOGLE_PLACES_API_KEY
"""

import time
import requests
from django.conf import settings


# =============================================================
# Interface base
# =============================================================

class GeocodingBackend:
    def autocomplete(self, query: str) -> list[dict]:
        raise NotImplementedError

    def place_details(self, place_id: str) -> dict | None:
        raise NotImplementedError


# =============================================================
# Backend Nominatim (OpenStreetMap) — gratuito, sem cadastro
# =============================================================

class NominatimBackend(GeocodingBackend):
    """
    Usa a API pública do Nominatim (OpenStreetMap).
    Limite: 1 req/segundo. Ideal para desenvolvimento e uso pessoal.
    Docs: https://nominatim.org/release-docs/develop/api/Search/
    """

    BASE_URL    = "https://nominatim.openstreetmap.org"
    USER_AGENT  = "PlanNGo/1.0 (contact@plango.app)"

    # Mapeamento de country_code ISO → nome do país em PT
    COUNTRY_NAMES = {
        "br": "Brasil",       "pt": "Portugal",      "us": "Estados Unidos",
        "ar": "Argentina",    "es": "Espanha",        "fr": "França",
        "de": "Alemanha",     "it": "Itália",         "jp": "Japão",
        "cn": "China",        "mx": "México",         "co": "Colômbia",
        "cl": "Chile",        "pe": "Peru",           "bo": "Bolívia",
        "py": "Paraguai",     "uy": "Uruguai",        "ve": "Venezuela",
        "ec": "Equador",      "gb": "Reino Unido",    "ca": "Canadá",
        "au": "Austrália",    "nz": "Nova Zelândia",  "za": "África do Sul",
        "in": "Índia",        "th": "Tailândia",      "id": "Indonésia",
        "vn": "Vietnã",       "kr": "Coreia do Sul",  "gr": "Grécia",
        "tr": "Turquia",      "eg": "Egito",          "ma": "Marrocos",
        "tz": "Tanzânia",     "ke": "Quênia",         "ng": "Nigéria",
        "np": "Nepal",        "lk": "Sri Lanka",      "mx": "México",
        "cr": "Costa Rica",   "pa": "Panamá",         "cu": "Cuba",
        "do": "Rep. Dominicana", "hn": "Honduras",    "gt": "Guatemala",
        "nl": "Holanda",      "be": "Bélgica",        "ch": "Suíça",
        "at": "Áustria",      "se": "Suécia",         "no": "Noruega",
        "dk": "Dinamarca",    "fi": "Finlândia",      "pl": "Polônia",
        "cz": "República Tcheca", "hu": "Hungria",    "ro": "Romênia",
        "ru": "Rússia",       "ua": "Ucrânia",        "il": "Israel",
        "sa": "Arábia Saudita", "ae": "Emirados Árabes", "sg": "Cingapura",
        "my": "Malásia",      "ph": "Filipinas",      "pk": "Paquistão",
        "bd": "Bangladesh",   "mm": "Myanmar",        "kh": "Camboja",
        "is": "Islândia",     "ie": "Irlanda",        "hr": "Croácia",
        "rs": "Sérvia",       "bg": "Bulgária",       "sk": "Eslováquia",
        "si": "Eslovênia",    "lt": "Lituânia",       "lv": "Letônia",
        "ee": "Estônia",      "by": "Bielorrússia",   "md": "Moldávia",
        "ge": "Geórgia",      "am": "Armênia",        "az": "Azerbaijão",
        "kz": "Cazaquistão",  "uz": "Uzbequistão",    "mn": "Mongólia",
        "la": "Laos",         "et": "Etiópia",        "gh": "Gana",
        "cm": "Camarões",     "ci": "Costa do Marfim","sn": "Senegal",
        "ug": "Uganda",       "zw": "Zimbábue",       "mz": "Moçambique",
        "ao": "Angola",       "na": "Namíbia",        "bw": "Botswana",
        "mg": "Madagascar",   "mu": "Maurício",       "re": "Reunião",
        "mx": "México",       "jm": "Jamaica",        "tt": "Trinidad e Tobago",
        "ba": "Bósnia",       "mk": "Macedônia",      "al": "Albânia",
        "mt": "Malta",        "cy": "Chipre",         "lu": "Luxemburgo",
        "li": "Liechtenstein","mc": "Mônaco",         "sm": "San Marino",
        "va": "Vaticano",     "ad": "Andorra",
    }

    # Mapeamento de country_code → continente
    CONTINENT_MAP = {
        "br": "América do Sul", "ar": "América do Sul", "cl": "América do Sul",
        "pe": "América do Sul", "co": "América do Sul", "ve": "América do Sul",
        "ec": "América do Sul", "bo": "América do Sul", "py": "América do Sul",
        "uy": "América do Sul", "gy": "América do Sul", "sr": "América do Sul",
        "us": "América do Norte", "ca": "América do Norte", "mx": "América do Norte",
        "gt": "América Central", "bz": "América Central", "hn": "América Central",
        "sv": "América Central", "ni": "América Central", "cr": "América Central",
        "pa": "América Central", "cu": "Caribe",          "do": "Caribe",
        "jm": "Caribe",         "ht": "Caribe",          "tt": "Caribe",
        "gb": "Europa",         "fr": "Europa",          "de": "Europa",
        "it": "Europa",         "es": "Europa",          "pt": "Europa",
        "nl": "Europa",         "be": "Europa",          "ch": "Europa",
        "at": "Europa",         "se": "Europa",          "no": "Europa",
        "dk": "Europa",         "fi": "Europa",          "pl": "Europa",
        "cz": "Europa",         "hu": "Europa",          "ro": "Europa",
        "gr": "Europa",         "tr": "Europa",          "ru": "Europa",
        "ua": "Europa",         "by": "Europa",          "rs": "Europa",
        "hr": "Europa",         "ba": "Europa",          "si": "Europa",
        "sk": "Europa",         "bg": "Europa",          "md": "Europa",
        "lt": "Europa",         "lv": "Europa",          "ee": "Europa",
        "is": "Europa",         "ie": "Europa",          "lu": "Europa",
        "mt": "Europa",         "cy": "Europa",          "al": "Europa",
        "mk": "Europa",         "me": "Europa",          "li": "Europa",
        "mc": "Europa",         "sm": "Europa",          "va": "Europa",
        "ad": "Europa",
        "cn": "Ásia",           "jp": "Ásia",            "in": "Ásia",
        "kr": "Ásia",           "id": "Ásia",            "th": "Ásia",
        "vn": "Ásia",           "ph": "Ásia",            "my": "Ásia",
        "sg": "Ásia",           "pk": "Ásia",            "bd": "Ásia",
        "np": "Ásia",           "lk": "Ásia",            "mm": "Ásia",
        "kh": "Ásia",           "la": "Ásia",            "mn": "Ásia",
        "kz": "Ásia",           "uz": "Ásia",            "ge": "Ásia",
        "am": "Ásia",           "az": "Ásia",            "il": "Ásia",
        "sa": "Ásia",           "ae": "Ásia",            "jo": "Ásia",
        "lb": "Ásia",           "sy": "Ásia",            "iq": "Ásia",
        "ir": "Ásia",           "af": "Ásia",            "ye": "Ásia",
        "om": "Ásia",           "kw": "Ásia",            "qa": "Ásia",
        "bh": "Ásia",
        "eg": "África",         "ma": "África",          "za": "África",
        "ng": "África",         "et": "África",          "gh": "África",
        "ke": "África",         "tz": "África",          "ug": "África",
        "cm": "África",         "ci": "África",          "sn": "África",
        "ao": "África",         "mz": "África",          "zw": "África",
        "bw": "África",         "na": "África",          "mg": "África",
        "mu": "África",         "dz": "África",          "tn": "África",
        "ly": "África",         "sd": "África",          "cd": "África",
        "ml": "África",         "bf": "África",
        "au": "Oceania",        "nz": "Oceania",         "pg": "Oceania",
        "fj": "Oceania",        "sb": "Oceania",         "vu": "Oceania",
        "ws": "Oceania",        "to": "Oceania",
    }

    def _headers(self):
        return {"User-Agent": self.USER_AGENT, "Accept-Language": "pt-BR,pt;q=0.9"}

    def autocomplete(self, query: str) -> list[dict]:
        if not query or len(query.strip()) < 2:
            return []

        params = {
            "q":              query,
            "format":         "json",
            "addressdetails": 1,
            "limit":          6,
            "featuretype":    "settlement",
        }

        try:
            response = requests.get(
                f"{self.BASE_URL}/search",
                params=params,
                headers=self._headers(),
                timeout=5,
            )
            response.raise_for_status()
            results = response.json()
        except requests.RequestException:
            return []

        suggestions = []
        seen = set()

        for r in results:
            address     = r.get("address", {})
            country_code = r.get("address", {}).get("country_code", "").lower()
            country     = self.COUNTRY_NAMES.get(country_code, address.get("country", ""))
            continent   = self.CONTINENT_MAP.get(country_code, "")

            # Nome principal do lugar
            name = (
                r.get("name")
                or address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("hamlet")
                or r.get("display_name", "").split(",")[0]
            )

            if not name or not country:
                continue

            key = f"{name.lower()}|{country_code}"
            if key in seen:
                continue
            seen.add(key)

            # Label exibido na lista de sugestões
            state = address.get("state", "")
            label = f"{name}, {state}, {country}" if state else f"{name}, {country}"

            suggestions.append({
                "place_id":   r.get("place_id"),
                "name":       name,
                "label":      label,
                "country":    country,
                "country_code": country_code.upper(),
                "continent":  continent,
                "lat":        r.get("lat"),
                "lon":        r.get("lon"),
                "source":     "nominatim",
            })

        return suggestions

    def place_details(self, place_id: str) -> dict | None:
        """Busca detalhes completos de um lugar pelo place_id do Nominatim."""
        try:
            response = requests.get(
                f"{self.BASE_URL}/details",
                params={"place_id": place_id, "format": "json", "addressdetails": 1},
                headers=self._headers(),
                timeout=5,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None


# =============================================================
# Backend Google Places API — requer chave no .env
# =============================================================

class GooglePlacesBackend(GeocodingBackend):
    """
    Usa a Google Places API (New).
    Requer: GOOGLE_PLACES_API_KEY no .env
    Docs: https://developers.google.com/maps/documentation/places/web-service

    Para ativar: GEOCODING_BACKEND=google no .env
    """

    AUTOCOMPLETE_URL = "https://places.googleapis.com/v1/places:autocomplete"
    DETAILS_URL      = "https://places.googleapis.com/v1/places/{place_id}"

    # Mapeamento região → continente (mesmo do Nominatim para consistência)
    CONTINENT_MAP = NominatimBackend.CONTINENT_MAP

    def _api_key(self):
        key = getattr(settings, "GOOGLE_PLACES_API_KEY", "")
        if not key:
            raise ValueError(
                "GOOGLE_PLACES_API_KEY não configurada. "
                "Adicione ao .env ou use GEOCODING_BACKEND=nominatim."
            )
        return key

    def autocomplete(self, query: str) -> list[dict]:
        if not query or len(query.strip()) < 2:
            return []

        try:
            response = requests.post(
                self.AUTOCOMPLETE_URL,
                headers={
                    "Content-Type":  "application/json",
                    "X-Goog-Api-Key": self._api_key(),
                },
                json={
                    "input":               query,
                    "languageCode":        "pt",
                    "includedPrimaryTypes": ["locality", "natural_feature",
                                            "tourist_attraction", "point_of_interest"],
                },
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException:
            return []

        suggestions = []
        for s in data.get("suggestions", []):
            pred = s.get("placePrediction", {})
            if not pred:
                continue

            place_id = pred.get("placeId", "")
            text     = pred.get("text", {}).get("text", "")
            parts    = [p.get("text", "") for p in pred.get("structuredFormat", {})
                        .get("secondaryText", {}).get("matches", [])]

            suggestions.append({
                "place_id": place_id,
                "name":     pred.get("structuredFormat", {})
                               .get("mainText", {}).get("text", text),
                "label":    text,
                "country":  "",    # preenchido via place_details
                "country_code": "",
                "continent": "",
                "lat":      None,
                "lon":      None,
                "source":   "google",
            })

        return suggestions

    def place_details(self, place_id: str) -> dict | None:
        """Busca detalhes e extrai país + continente."""
        try:
            response = requests.get(
                self.DETAILS_URL.format(place_id=place_id),
                headers={
                    "X-Goog-Api-Key": self._api_key(),
                    "X-Goog-FieldMask": "id,displayName,addressComponents,"
                                        "location,formattedAddress",
                },
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException:
            return None

        country      = ""
        country_code = ""

        for comp in data.get("addressComponents", []):
            if "country" in comp.get("types", []):
                country      = comp.get("longText", "")
                country_code = comp.get("shortText", "").lower()
                break

        continent = self.CONTINENT_MAP.get(country_code, "")
        location  = data.get("location", {})

        return {
            "place_id":     place_id,
            "name":         data.get("displayName", {}).get("text", ""),
            "country":      country,
            "country_code": country_code.upper(),
            "continent":    continent,
            "lat":          location.get("latitude"),
            "lon":          location.get("longitude"),
            "source":       "google",
        }


# =============================================================
# Factory — seleciona o backend pelo .env
# =============================================================

def get_geocoding_backend() -> GeocodingBackend:
    """
    Retorna o backend configurado em GEOCODING_BACKEND no .env.
    Padrão: nominatim
    """
    backend = getattr(settings, "GEOCODING_BACKEND", "nominatim").lower()

    if backend == "google":
        return GooglePlacesBackend()

    return NominatimBackend()
