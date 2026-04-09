# Busca de Imagens

O Plan N'Go busca automaticamente uma foto do destino ao importar por URL ou texto.
Atualmente usa o **Unsplash API** (padrão). O **Google Custom Search** está disponível como alternativa futura.

---

## Backend ativo: Unsplash API

### Por que Unsplash?

| | Unsplash | Google Custom Search |
|---|---|---|
| Cadastro | Sim (gratuito) | Sim (gratuito) |
| Billing obrigatório | Não | Sim |
| Limite gratuito | 50 req/hora | 100 req/dia |
| Qualidade das fotos | Alta (fotógrafos profissionais) | Variável |
| Complexidade de setup | Baixa | Alta |

---

## Tutorial — Configurar o Unsplash API

### Passo 1 — Criar conta de desenvolvedor

1. Acesse [unsplash.com/developers](https://unsplash.com/developers)
2. Clique em **Register as a developer**
3. Faça login ou crie uma conta gratuita

### Passo 2 — Criar uma aplicação

1. Clique em **New Application**
2. Aceite os termos de uso
3. Preencha:
   - **Application name**: `Plan N Go`
   - **Description**: `Travel destination catalog app`
4. Clique em **Create application**

### Passo 3 — Obter a chave

Na página da aplicação, copie o **Access Key** (não a Secret Key).

```
Access Key: knlnQHGOQVms...
Secret Key: AbxQuwFoeHh... (não é necessária)
```

### Passo 4 — Configurar no projeto

Adicione ao `.env`:

```bash
UNSPLASH_ACCESS_KEY=sua-access-key-aqui
```

Adicione ao `plango/settings.py` (já incluído no setup):

```python
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")
```

### Passo 5 — Testar

```bash
cd ~/workspace/plan-n-go
python manage.py shell -c "
from destinations.image_search import search_destination_image
url = search_destination_image('Kyoto', 'Japão')
print('URL:', url[:80] if url else 'nenhuma')
"
```

---

## Como funciona no código

Localização: `destinations/image_search.py`

```python
from destinations.image_search import search_destination_image

# Busca uma foto landscape do destino
url = search_destination_image("Machu Picchu", "Peru")
# → https://images.unsplash.com/photo-...
```

A função é chamada automaticamente pelo `importer.py` após a extração dos dados pelo Gemini/Claude, quando não há imagem disponível no conteúdo original.

### Fluxo completo

```
Texto colado pelo usuário
        ↓
Gemini extrai dados do destino
        ↓
Tem imagem no conteúdo? → Usa a imagem do conteúdo
        ↓ não
search_destination_image(name, country)
        ↓
Unsplash API → foto landscape de alta qualidade
        ↓
Modal pré-preenchido com a imagem
```

---

## Limites do plano gratuito

| Limite | Valor |
|---|---|
| Requisições por hora | 50 |
| Requisições por mês | Ilimitado (dentro do limite/hora) |
| Uso comercial | Permitido com atribuição |
| Qualidade máxima | 1080px (plano gratuito) |

Para produção com alto volume, considere o plano **Production** (aprovação necessária pela Unsplash).

---

## Atribuição obrigatória

Os termos do Unsplash exigem que você exiba o nome do fotógrafo quando usar as fotos. Para o Plan N'Go, isso é recomendado na página de detalhes do destino.

A API retorna os dados do fotógrafo:

```python
response = requests.get("https://api.unsplash.com/search/photos", ...)
result = response.json()["results"][0]

foto_url        = result["urls"]["regular"]
fotografo_nome  = result["user"]["name"]
fotografo_link  = result["user"]["links"]["html"]
```

---

## Alternativa futura: Google Custom Search API

> ⚠️ Esta seção é para referência futura. O backend ativo é o Unsplash.

### Quando usar o Google Custom Search?

- Quando precisar de imagens de sites específicos (TripAdvisor, Booking, etc.)
- Quando o Unsplash não tiver fotos do destino
- Em produção com alto volume (100 req/dia grátis, sem limite por hora)

### Configuração

**Passo 1 — Ativar no Google Cloud**

1. Acesse [console.cloud.google.com](https://console.cloud.google.com)
2. Selecione o projeto do Plan N'Go
3. **APIs & Services** → **Library** → busque **Custom Search API** → **Enable**
4. O projeto precisa ter **billing ativado** (não cobra nas primeiras 100 req/dia)

**Passo 2 — Criar o mecanismo de busca**

1. Acesse [programmablesearchengine.google.com](https://programmablesearchengine.google.com)
2. **New search engine**
3. Adicione os sites: `unsplash.com`, `flickr.com`, `wikimedia.org`, `nationalgeographic.com`, `travelandleisure.com`, `lonelyplanet.com`
4. Em **Search Features** → ative **Image search**
5. Copie o **Search Engine ID (cx)**

> ⚠️ A opção "Search the entire web" foi descontinuada pelo Google em 2025. É necessário especificar os sites manualmente.

**Passo 3 — Criar a chave de API**

1. **APIs & Services** → **Credentials** → **+ Create Credentials** → **API Key**
2. Restrinja a chave para **Custom Search API**
3. Copie a chave

> ⚠️ A chave deve ser criada **no mesmo projeto** onde a API foi habilitada.

**Passo 4 — Configurar no projeto**

```bash
GOOGLE_CUSTOM_SEARCH_KEY=sua-chave-aqui
GOOGLE_CUSTOM_SEARCH_CX=seu-cx-aqui
```

**Passo 5 — Ativar no código**

Para usar o Google Custom Search, atualize `destinations/image_search.py`:

```python
def search_destination_image(destination_name: str, country: str = "") -> str:
    api_key = getattr(settings, "GOOGLE_CUSTOM_SEARCH_KEY", "")
    cx      = getattr(settings, "GOOGLE_CUSTOM_SEARCH_CX", "")

    if not api_key or not cx:
        return ""

    query = f"{destination_name} {country} travel landscape"

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

    data  = response.json()
    items = data.get("items", [])
    return items[0].get("link", "") if items else ""
```

---

## Trocar de backend

Para trocar de Unsplash para Google (ou vice-versa), edite `destinations/image_search.py` conforme os exemplos acima. Não há variável de ambiente para isso — é uma alteração direta no código.
