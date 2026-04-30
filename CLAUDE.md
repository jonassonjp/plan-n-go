# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Dev server
python manage.py runserver

# Migrations
python manage.py makemigrations
python manage.py migrate

# Run all tests (with coverage, verbose — configured in pytest.ini)
pytest

# Run a specific app's tests
pytest accounts/tests/ -v
pytest roteiros/tests.py -v

# Run only unit tests (skip acceptance/Playwright)
pytest --ignore=tests/acceptance/

# Run acceptance tests (requires live server at localhost:8000 and a seeded test user)
pytest tests/acceptance/ -v

# Lint
flake8 .

# Format
black .
isort .

# Collect static files
python manage.py collectstatic
```

## Environment

Copy `.env.example` to `.env`. Key variables:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key |
| `ANTHROPIC_API_KEY` | Claude API for AI itinerary generation |
| `AI_BACKEND` | `gemini` (default) or `anthropic` |
| `GEMINI_API_KEY` | Gemini API key |
| `GEOCODING_BACKEND` | `nominatim` (free, default) or `google` |
| `GOOGLE_PLACES_API_KEY` | Required only if `GEOCODING_BACKEND=google` |
| `UNSPLASH_ACCESS_KEY` | Image search |
| `DATABASE_URL` | PostgreSQL in prod; omit to use SQLite in dev |
| `FRONTEND_URL` | CORS origin for the React frontend (default: `http://localhost:5173`) |

## Architecture

Django 6.0 + Python 3.13 server-side rendered app. Templates live in `templates/` (global) and `templates/<app>/`. The frontend is Tailwind CSS via CDN with vanilla JS — there is no separate React build step in dev; React + TypeScript is planned for later.

### Django Apps

| App | Role |
|---|---|
| `accounts` | Custom `User` model (email-based auth, UUID token for email verification). Auth backend: `EmailAuthBackend`. Login requires email confirmation (`is_active=False` until verified). |
| `destinations` | Per-user travel destination catalogue. `Destination` supports photo upload or external URL, JSONField for languages/best_months/vaccines, geocoding autocomplete via pluggable backends. |
| `lists` | `DestinationList` — manual (M2M via `ListItem` with position) or smart (filter by continent/country/language/month stored in `smart_criteria` JSONField). |
| `roteiros` | Itineraries. `Roteiro → Dia → Indicacao` hierarchy. Supports AI generation via Anthropic Claude (`generate_ai` view calls `_gerar_roteiro_claude`). Cost tracking in local currency with BRL conversion via `taxa_cambio`. |
| `feed` | `FeaturedDestination` — curated public destinations managed by superusers, shown on landing page. |

### URL Structure

```
/                    → landing page (plango.views.index)
/accounts/           → auth (login, register, verify, profile)
/destinations/       → destination CRUD + autocomplete API
/lists/              → list CRUD + add/remove destinations
/roteiros/           → itinerary CRUD + AI generation
/feed/               → featured destinations (public)
/admin/              → Django admin
```

### Key Design Decisions

- **Custom user model** (`accounts.User`): uses `email` as `USERNAME_FIELD`, not `username`. Always use `get_user_model()` instead of importing `User` directly.
- **Geocoding is pluggable**: `destinations/geocoding.py` defines a `GeocodingBackend` interface with Nominatim and Google implementations. Selected via `GEOCODING_BACKEND` env var.
- **AI backend**: `roteiros/views.py::_gerar_roteiro_claude` calls Anthropic Claude synchronously in the request cycle. The model hardcoded is `claude-sonnet-4-20250514`. Requires `ANTHROPIC_API_KEY`.
- **Static files**: WhiteNoise serves them in production. In dev, `STATICFILES_DIRS = [BASE_DIR / "static"]`. Global CSS is in `static/css/`, app-specific in e.g. `static/css/roteiros.css`.
- **Templates**: Global components in `templates/components/`. App templates in `templates/<app>/`. Base template: `templates/plango/base.html`.
- **Tests**: Unit tests live inside each app (`accounts/tests/`, `destinations/tests.py`, etc.). Acceptance/E2E tests (Playwright) are in `tests/acceptance/` and need a live server with a seeded user (`teste@plango.app` / `senha@1234`).
- **REST API**: DRF + SimpleJWT used alongside server-rendered views. JWT tokens: 1-hour access, 30-day refresh with rotation. Session auth also supported (for browser access to API).
