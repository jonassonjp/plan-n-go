"""
Plan N'Go — Serviço de importação por URL
Suporta: blogs, sites de viagem, TripAdvisor, Booking, etc.
Fluxo: scraping → Claude API → dados estruturados
"""

import re
import json
import requests
from bs4 import BeautifulSoup
from anthropic import Anthropic
from .image_search import search_destination_image


# =============================================================
# Scraping
# =============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Sites que funcionam bem
SUPPORTED_DOMAINS = [
    "tripadvisor", "booking.com", "expedia", "timeout",
    "viajabi", "mochileiros", "malucos", "dicasdeviagem",
    "viagemeturismo", "melhoresdestinos", "viajeaqui",
    "guiaviajem", "blogdeviagem", "vivadecay", "turistando",
    "wordpress", "blogspot", "medium", "substack",
]


def scrape_url(url: str) -> dict:
    """
    Faz scraping da URL e retorna o conteúdo textual extraído.
    """
    url = url.strip()

    # Bloquear Instagram
    if "instagram.com" in url:
        raise ScrapingError(
            "O Instagram não permite extração automática de conteúdo. "
            "Use a opção de texto livre para colar a legenda manualmente."
        )

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ScrapingError(f"Não foi possível acessar a URL: {e}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Remover scripts, estilos e navegação
    for tag in soup(["script", "style", "nav", "header", "footer",
                     "aside", "form", "button", "iframe"]):
        tag.decompose()

    return _scrape_generic(url, soup)


def _scrape_generic(url: str, soup: BeautifulSoup) -> dict:
    """Extrai dados de blog ou site de viagem."""
    text_parts = []
    image_url  = ""

    # Meta tags OG (mais ricas)
    og_title = soup.find("meta", property="og:title")
    og_desc  = soup.find("meta", property="og:description")
    og_image = soup.find("meta", property="og:image")
    meta_desc = soup.find("meta", attrs={"name": "description"})

    if og_title and og_title.get("content"):
        text_parts.append(og_title["content"])
    if og_desc and og_desc.get("content"):
        text_parts.append(og_desc["content"])
    elif meta_desc and meta_desc.get("content"):
        text_parts.append(meta_desc["content"])
    if og_image and og_image.get("content"):
        image_url = og_image["content"]

    # Título H1
    h1 = soup.find("h1")
    if h1:
        text_parts.append(h1.get_text(strip=True))

    # Subtítulos H2
    for h2 in soup.find_all("h2")[:5]:
        t = h2.get_text(strip=True)
        if t:
            text_parts.append(t)

    # Conteúdo principal — tenta article, main, div com classe de conteúdo
    main_content = (
        soup.find("article") or
        soup.find("main") or
        soup.find(class_=re.compile(r"(post|content|article|entry|texto|conteudo)", re.I)) or
        soup.find("body")
    )

    if main_content:
        paragraphs = main_content.find_all("p")
        for p in paragraphs[:20]:
            t = p.get_text(strip=True)
            if len(t) > 50:
                text_parts.append(t)

    text = " ".join(text_parts).strip()

    # Limitar para não exceder contexto do Claude
    text = text[:4000]

    if not text or len(text) < 50:
        raise ScrapingError(
            "Não foi possível extrair conteúdo da página. "
            "Verifique se a URL está correta e tente novamente."
        )

    return {
        "url":         url,
        "text":        text,
        "title":       og_title["content"] if og_title and og_title.get("content") else "",
        "image_url":   image_url,
        "source_type": "web",
    }


# =============================================================
# Texto livre (fallback manual)
# =============================================================

def scrape_from_text(text: str, url: str = "") -> dict:
    """
    Permite o usuário colar o texto diretamente (legenda, descrição, etc.)
    em vez de uma URL.
    """
    if not text or len(text.strip()) < 20:
        raise ScrapingError("O texto é muito curto para identificar um destino.")

    return {
        "url":         url,
        "text":        text.strip()[:4000],
        "title":       "",
        "image_url":   "",
        "source_type": "text",
    }


# =============================================================
# Claude API — extração estruturada
# =============================================================

SYSTEM_PROMPT = """Você é um assistente especializado em viagens.
Analise o texto fornecido e extraia informações sobre destinos de viagem.
Responda APENAS com um objeto JSON válido, sem texto antes ou depois, sem markdown.
Se não tiver certeza sobre algum campo, use null.
Para campos de lista, use array vazio [] se não encontrar informação."""

EXTRACTION_PROMPT = """Analise este texto sobre viagem e extraia as informações do destino principal.

Texto:
{text}

URL de origem: {url}

Retorne um JSON com exatamente esta estrutura:
{{
  "name": "nome do local/destino principal",
  "country": "país em português (ex: Peru, Japão, França)",
  "continent": "continente em português (ex: América do Sul, Ásia, Europa)",
  "description": "descrição resumida do destino extraída do texto (máx 300 chars)",
  "languages": ["idioma1", "idioma2"],
  "currency": "código da moeda (ex: BRL, USD, EUR, JPY)",
  "best_months": [lista de números 1-12 dos melhores meses],
  "visa_required": true/false/null,
  "visa_type": "tipo de visto se mencionado ou null",
  "vaccination_required": true/false/null,
  "vaccines": ["vacina1"],
  "vaccines_notes": "observações sobre vacinas ou vazio",
  "other_requirements_title": "outra exigência ou vazio",
  "other_requirements_description": "descrição da exigência ou vazio",
  "confidence": "high/medium/low",
  "extraction_notes": "o que foi identificado e o que ficou incerto"
}}

Vacinas válidas: febre_amarela, covid, hepatite_a, hepatite_b, tifoide, colera, meningite, raiva, encefalite, poliomielite, outra
Idiomas válidos: Português, Inglês, Espanhol, Francês, Alemão, Italiano, Japonês, Mandarim, Coreano, Árabe, Hindi, Russo, Grego, Holandês, Sueco, Tailandês, Vietnamita, Indonésio"""


def extract_with_claude(scraped: dict) -> dict:
    client = Anthropic()

    prompt = EXTRACTION_PROMPT.format(
        text=scraped["text"][:3000],
        url=scraped.get("url", ""),
    )

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*",     "", raw)
    raw = re.sub(r"\s*```$",     "", raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ExtractionError(f"Resposta inválida do Claude: {e}")

    # Usar imagem do scraping se disponível
    if scraped.get("image_url"):
        data["image_url"] = scraped["image_url"]
    else:
        # Buscar imagem via Google Custom Search
        name    = data.get("name", "")
        country = data.get("country", "")
        if name:
            img_url = search_destination_image(name, country)
            if img_url:
                data["image_url"] = img_url

    data["source_url"] = scraped.get("url", "")

    return data


# =============================================================
# Pipelines principais
# =============================================================

def import_from_url(url: str) -> dict:
    """URL → scraping → Claude → dados estruturados."""
    scraped = scrape_url(url)
    return extract_with_claude(scraped)


def import_from_text(text: str, url: str = "") -> dict:
    """Texto livre → Claude → dados estruturados."""
    scraped = scrape_from_text(text, url)
    return extract_with_claude(scraped)


# =============================================================
# Exceções
# =============================================================

class ScrapingError(Exception):
    pass

class ExtractionError(Exception):
    pass
