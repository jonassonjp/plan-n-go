"""
Plan N'Go — Serviço de importação por URL
Suporta dois backends de IA: Gemini (gratuito) e Anthropic (pago).

Configuração no .env:
  AI_BACKEND=gemini     # padrão, gratuito, 1500 req/dia
  AI_BACKEND=anthropic  # pago, mais preciso
"""

import re
import json
import requests
from bs4 import BeautifulSoup
from django.conf import settings


# =============================================================
# Scraping
# =============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "DNT": "1",
}


def _scrape_request(url: str) -> requests.Response:
    """Faz a requisição usando sessão com cookies para parecer mais com um browser real."""
    session = requests.Session()
    session.headers.update(HEADERS)

    # Primeira requisição à homepage do domínio para obter cookies de sessão
    from urllib.parse import urlparse
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    try:
        session.get(origin, timeout=8, allow_redirects=True)
    except Exception:
        pass  # ignora falha na requisição de aquecimento

    # Requisição principal com Referer setado
    session.headers["Referer"] = origin + "/"
    response = session.get(url, timeout=12, allow_redirects=True)
    return response


def scrape_url(url: str) -> dict:
    url = url.strip()

    if "instagram.com" in url:
        raise ScrapingError(
            "O Instagram não permite extração automática de conteúdo. "
            "Use a opção 'Colar texto' para colar a legenda manualmente."
        )

    try:
        response = _scrape_request(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else None
        if status == 403:
            raise ScrapingError(
                "O site bloqueou o acesso automático (erro 403). "
                "Isso é comum em grandes portais de turismo. "
                "Tente a opção 'Colar texto': copie o conteúdo da página e cole diretamente."
            )
        if status == 404:
            raise ScrapingError(
                "Página não encontrada (erro 404). Verifique se a URL está correta."
            )
        if status in (429, 503):
            raise ScrapingError(
                "O site está temporariamente indisponível ou limitou os acessos. "
                "Aguarde alguns minutos e tente novamente, ou use a opção 'Colar texto'."
            )
        raise ScrapingError(f"Erro ao acessar a URL (HTTP {status}). Tente a opção 'Colar texto'.")
    except requests.exceptions.ConnectionError:
        raise ScrapingError(
            "Não foi possível conectar ao site. Verifique se a URL está correta e tente novamente."
        )
    except requests.exceptions.Timeout:
        raise ScrapingError(
            "O site demorou demais para responder. Tente novamente ou use a opção 'Colar texto'."
        )
    except requests.RequestException as e:
        raise ScrapingError(f"Erro ao acessar a URL: {e}")

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "header", "footer",
                     "aside", "form", "button", "iframe"]):
        tag.decompose()

    return _scrape_generic(url, soup)


def _scrape_generic(url: str, soup: BeautifulSoup) -> dict:
    text_parts = []
    image_url  = ""

    og_title  = soup.find("meta", property="og:title")
    og_desc   = soup.find("meta", property="og:description")
    og_image  = soup.find("meta", property="og:image")
    meta_desc = soup.find("meta", attrs={"name": "description"})

    if og_title and og_title.get("content"):
        text_parts.append(og_title["content"])
    if og_desc and og_desc.get("content"):
        text_parts.append(og_desc["content"])
    elif meta_desc and meta_desc.get("content"):
        text_parts.append(meta_desc["content"])
    if og_image and og_image.get("content"):
        image_url = og_image["content"]

    h1 = soup.find("h1")
    if h1:
        text_parts.append(h1.get_text(strip=True))

    for h2 in soup.find_all("h2")[:5]:
        t = h2.get_text(strip=True)
        if t:
            text_parts.append(t)

    main_content = (
        soup.find("article") or
        soup.find("main") or
        soup.find(class_=re.compile(r"(post|content|article|entry|texto|conteudo)", re.I)) or
        soup.find("body")
    )

    if main_content:
        for p in main_content.find_all("p")[:20]:
            t = p.get_text(strip=True)
            if len(t) > 50:
                text_parts.append(t)

    text = " ".join(text_parts).strip()[:4000]

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


def scrape_from_text(text: str, url: str = "") -> dict:
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
# Prompt compartilhado
# =============================================================

SYSTEM_PROMPT = """Você é um assistente especializado em viagens.
Analise o texto fornecido e extraia informações sobre destinos de viagem.
Responda APENAS com um objeto JSON válido, sem texto antes ou depois, sem markdown."""

EXTRACTION_PROMPT = """Analise este texto sobre viagem e extraia as informações do destino principal.

Texto:
{text}

URL de origem: {url}

Retorne um JSON com exatamente esta estrutura:
{{
  "name": "nome do local/destino principal",
  "country": "país em português (ex: Peru, Japão, França)",
  "continent": "continente em português (ex: América do Sul, Ásia, Europa)",
  "description": "descrição resumida do destino (máx 300 chars)",
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


def _parse_json(raw: str) -> dict:
    """Limpa e parseia JSON retornado pela IA."""
    raw = re.sub(r"^```json\s*", "", raw.strip())
    raw = re.sub(r"^```\s*",     "", raw)
    raw = re.sub(r"\s*```$",     "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ExtractionError(f"Resposta JSON inválida: {e}")


# =============================================================
# Backend Gemini (gratuito — padrão)
# =============================================================

def _extract_with_gemini(scraped: dict) -> dict:
    """Usa Google Gemini para extrair dados do destino."""
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if not api_key:
        raise ExtractionError("GEMINI_API_KEY não configurada no .env.")

    prompt = SYSTEM_PROMPT + "\n\n" + EXTRACTION_PROMPT.format(
        text=scraped["text"][:3000],
        url=scraped.get("url", ""),
    )

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}",
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature":     0.1,
                "maxOutputTokens": 2000,
            },
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise ExtractionError(f"Erro na API Gemini: {response.status_code} — {response.text[:200]}")

    data     = response.json()
    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]

    return _parse_json(raw_text)


# =============================================================
# Backend Anthropic (pago — opcional)
# =============================================================

def _extract_with_anthropic(scraped: dict) -> dict:
    """Usa Anthropic Claude para extrair dados do destino."""
    from anthropic import Anthropic

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

    return _parse_json(message.content[0].text)


# =============================================================
# Factory — seleciona backend pelo .env
# =============================================================

def extract_with_ai(scraped: dict) -> dict:
    """
    Extrai dados do destino usando o backend configurado em AI_BACKEND.
    Padrão: gemini
    """
    backend = getattr(settings, "AI_BACKEND", "gemini").lower()

    if backend == "anthropic":
        data = _extract_with_anthropic(scraped)
    else:
        data = _extract_with_gemini(scraped)

    # Buscar imagem automaticamente se não houver
    if scraped.get("image_url"):
        data["image_url"] = scraped["image_url"]
    else:
        try:
            from .image_search import search_destination_image
            name    = data.get("name", "")
            country = data.get("country", "")
            if name:
                img_url = search_destination_image(name, country)
                if img_url:
                    data["image_url"] = img_url
        except Exception:
            pass

    data["source_url"] = scraped.get("url", "")
    return data


# Manter compatibilidade com código existente
def extract_with_claude(scraped: dict) -> dict:
    return extract_with_ai(scraped)


# =============================================================
# Pipelines principais
# =============================================================

def import_from_url(url: str) -> dict:
    scraped = scrape_url(url)
    return extract_with_ai(scraped)


def import_from_text(text: str, url: str = "") -> dict:
    scraped = scrape_from_text(text, url)
    return extract_with_ai(scraped)


# =============================================================
# Exceções
# =============================================================

class ScrapingError(Exception):
    pass

class ExtractionError(Exception):
    pass
