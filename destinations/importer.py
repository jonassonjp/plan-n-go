"""
Plan N'Go — Serviço de importação por URL
Suporta: Instagram (páginas públicas)
Fluxo: scraping → Claude API → dados estruturados
"""

import re
import json
import requests
from bs4 import BeautifulSoup
from anthropic import Anthropic


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
}


def scrape_url(url: str) -> dict:
    """
    Faz scraping da URL e retorna o conteúdo textual extraído.
    Retorna: { "url", "text", "title", "image_url", "source_type" }
    """
    url = url.strip()
    source_type = _detect_source(url)

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ScrapingError(f"Não foi possível acessar a URL: {e}")

    soup = BeautifulSoup(response.text, "html.parser")

    if source_type == "instagram":
        return _scrape_instagram(url, soup)
    else:
        return _scrape_generic(url, soup)


def _detect_source(url: str) -> str:
    if "instagram.com" in url:
        return "instagram"
    if "tripadvisor.com" in url or "tripadvisor.com.br" in url:
        return "tripadvisor"
    return "generic"


def _scrape_instagram(url: str, soup: BeautifulSoup) -> dict:
    """Extrai dados de post público do Instagram."""
    text_parts = []
    image_url  = ""

    # Meta tags (mais confiável no Instagram)
    og_desc = soup.find("meta", property="og:description")
    og_title = soup.find("meta", property="og:title")
    og_image = soup.find("meta", property="og:image")

    if og_desc and og_desc.get("content"):
        text_parts.append(og_desc["content"])
    if og_title and og_title.get("content"):
        text_parts.append(og_title["content"])
    if og_image and og_image.get("content"):
        image_url = og_image["content"]

    # Fallback: script tags com dados JSON
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, dict):
                caption = data.get("caption") or data.get("description") or ""
                if caption:
                    text_parts.append(caption)
        except (json.JSONDecodeError, AttributeError):
            pass

    text = " ".join(text_parts).strip()

    if not text:
        raise ScrapingError(
            "Não foi possível extrair conteúdo do post. "
            "Verifique se o perfil é público e a URL está correta."
        )

    return {
        "url":         url,
        "text":        text,
        "title":       og_title["content"] if og_title else "",
        "image_url":   image_url,
        "source_type": "instagram",
    }


def _scrape_generic(url: str, soup: BeautifulSoup) -> dict:
    """Extrai dados de blog ou site genérico."""
    text_parts = []
    image_url  = ""

    # Meta tags
    og_desc  = soup.find("meta", property="og:description")
    og_title = soup.find("meta", property="og:title")
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

    # Título da página
    if soup.title:
        text_parts.append(soup.title.string or "")

    # Parágrafos principais do artigo
    article = soup.find("article") or soup.find("main") or soup.find("body")
    if article:
        paragraphs = article.find_all("p")
        text_parts.extend(
            p.get_text(strip=True)
            for p in paragraphs[:10]
            if len(p.get_text(strip=True)) > 40
        )

    text = " ".join(text_parts).strip()[:4000]  # Limitar para Claude

    if not text:
        raise ScrapingError("Não foi possível extrair conteúdo da página.")

    return {
        "url":         url,
        "text":        text,
        "title":       og_title["content"] if og_title else "",
        "image_url":   image_url,
        "source_type": "generic",
    }


# =============================================================
# Claude API — extração estruturada
# =============================================================

SYSTEM_PROMPT = """Você é um assistente especializado em viagens.
Analise o texto fornecido e extraia informações sobre destinos de viagem.
Responda APENAS com um objeto JSON válido, sem texto antes ou depois, sem markdown.

Se não tiver certeza sobre algum campo, use null.
Para campos de lista, use array vazio [] se não encontrar informação.
"""

EXTRACTION_PROMPT = """Analise este texto de uma publicação sobre viagem e extraia as informações do destino mencionado.

Texto:
{text}

URL de origem: {url}

Retorne um JSON com exatamente esta estrutura:
{{
  "name": "nome do local/destino principal mencionado",
  "country": "país em português (ex: Peru, Japão, França)",
  "continent": "continente em português (ex: América do Sul, Ásia, Europa)",
  "description": "descrição do destino extraída ou resumida do texto (máx 300 chars)",
  "languages": ["idioma1", "idioma2"],
  "currency": "código da moeda (ex: BRL, USD, EUR, JPY)",
  "best_months": [lista de números 1-12 dos melhores meses mencionados ou típicos],
  "visa_required": true/false/null,
  "visa_type": "tipo de visto se mencionado",
  "vaccination_required": true/false/null,
  "vaccines": ["vacina1", "vacina2"],
  "vaccines_notes": "observações sobre vacinas",
  "other_requirements_title": "outra exigência se mencionada (ex: ETIAS)",
  "other_requirements_description": "descrição da exigência",
  "confidence": "high/medium/low",
  "extraction_notes": "observações sobre a extração"
}}

Vacinas válidas: febre_amarela, covid, hepatite_a, hepatite_b, tifoide, colera, meningite, raiva, encefalite, poliomielite, outra
Idiomas válidos: Português, Inglês, Espanhol, Francês, Alemão, Italiano, Japonês, Mandarim, Coreano, Árabe, Hindi, Russo, Grego, Holandês, Sueco, Tailandês, Vietnamita, Indonésio
"""


def extract_with_claude(scraped: dict) -> dict:
    """
    Envia o texto extraído para o Claude e retorna os dados estruturados.
    """
    client = Anthropic()

    prompt = EXTRACTION_PROMPT.format(
        text=scraped["text"][:3000],
        url=scraped["url"],
    )

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # Limpar possíveis backticks de markdown
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*",     "", raw)
    raw = re.sub(r"\s*```$",     "", raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ExtractionError(f"Claude retornou JSON inválido: {e}\n{raw}")

    # Adicionar imagem e URL de origem
    if scraped.get("image_url") and not data.get("image_url"):
        data["image_url"] = scraped["image_url"]
    data["source_url"] = scraped["url"]

    return data


# =============================================================
# Pipeline principal
# =============================================================

def import_from_url(url: str) -> dict:
    """
    Pipeline completo: URL → scraping → Claude → dados estruturados.
    Retorna dict pronto para pré-preencher o modal de destino.
    """
    scraped = scrape_url(url)
    data    = extract_with_claude(scraped)
    return data


# =============================================================
# Exceções
# =============================================================

class ScrapingError(Exception):
    pass

class ExtractionError(Exception):
    pass
