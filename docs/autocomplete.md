# Autocomplete de Destinos

## Visão geral

Ao digitar no campo "Nome do local", o sistema sugere destinos em tempo real.  
Ao selecionar uma sugestão, os campos de país, continente e idiomas são preenchidos automaticamente.

---

## Backends disponíveis

### Nominatim (padrão — gratuito)

- Usa a API pública do OpenStreetMap
- **Não requer cadastro nem chave de API**
- Limite: 1 requisição/segundo
- Cobre mais de 200 países, cidades, cachoeiras, pontos turísticos

### Google Places API (opcional)

- Requer chave no Google Cloud Console
- 10.000 requisições gratuitas/mês
- Resultados mais precisos e atualizados

---

## Configuração no `.env`

```bash
# Usar Nominatim (padrão):
GEOCODING_BACKEND=nominatim

# Usar Google Places:
GEOCODING_BACKEND=google
GOOGLE_PLACES_API_KEY=sua-chave-aqui
```

---

## Como funciona

```
usuário digita 2+ caracteres
        ↓ (debounce 400ms)
GET /destinations/autocomplete/?q=machu
        ↓
Django → NominatimBackend.autocomplete()
        ↓
Nominatim API → lista de lugares
        ↓
JSON com nome, país, continente, lat, lon
        ↓
Dropdown com sugestões
        ↓
usuário seleciona → campos preenchidos automaticamente
```

---

## Endpoints AJAX

### Autocomplete

```
GET /destinations/autocomplete/?q=<query>
```

Resposta:

```json
{
  "suggestions": [
    {
      "place_id": 123456,
      "name": "Machu Picchu",
      "label": "Machu Picchu, Cusco, Peru",
      "country": "Peru",
      "country_code": "PE",
      "continent": "América do Sul",
      "lat": "-13.1631",
      "lon": "-72.5450",
      "source": "nominatim"
    }
  ]
}
```

### Detalhes do lugar

```
GET /destinations/place-details/?place_id=<id>
```

---

## Preenchimento automático de idiomas

Ao selecionar um destino, os idiomas do país são ativados automaticamente nos botões de toggle.

Exemplos:
- Peru → Espanhol
- Brasil → Português
- Canadá → Inglês + Francês
- Índia → Hindi + Inglês
- Suíça → Francês + Alemão + Italiano

O usuário pode ajustar manualmente após o preenchimento automático.

---

## Arquitetura do código

Localização: `destinations/geocoding.py`

```python
# Interface base
class GeocodingBackend:
    def autocomplete(query) → list[dict]
    def place_details(place_id) → dict | None

# Implementações
class NominatimBackend(GeocodingBackend): ...
class GooglePlacesBackend(GeocodingBackend): ...

# Factory — lê GEOCODING_BACKEND do .env
def get_geocoding_backend() → GeocodingBackend
```

Para trocar de backend, basta mudar a variável no `.env` — nenhuma alteração de código necessária.

---

## Navegação por teclado

| Tecla     | Ação                              |
|-----------|-----------------------------------|
| ↓         | Próxima sugestão                  |
| ↑         | Sugestão anterior                 |
| Enter     | Selecionar sugestão destacada     |
| Escape    | Fechar dropdown                   |
