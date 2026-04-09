# Plan N'Go 🌍

> Catalogue seus destinos dos sonhos, planeje roteiros com IA e compartilhe suas viagens.

---

## Stack

| Camada      | Tecnologia                                      |
|-------------|------------------------------------------------|
| Backend     | Python 3.13 + Django 6.0.3                     |
| API         | Django REST Framework + SimpleJWT              |
| Banco (dev) | SQLite                                         |
| Banco (prod)| PostgreSQL                                     |
| IA          | Anthropic Claude API                           |
| Geocoding   | Nominatim (padrão, gratuito) / Google Places   |
| Frontend    | React + TypeScript + Tailwind CSS              |
| Static      | WhiteNoise                                     |

---

## Apps Django

| App            | Responsabilidade                                      |
|----------------|-------------------------------------------------------|
| `accounts`     | Cadastro, autenticação por e-mail e perfil            |
| `destinations` | Catálogo de destinos do usuário                       |
| `lists`        | Listas manuais e inteligentes *(em desenvolvimento)*  |
| `itineraries`  | Roteiros com IA *(em desenvolvimento)*                |
| `feed`         | Destinos públicos e exploração                        |

---

## Funcionalidades implementadas

| Módulo                          | Documento                                         |
|---------------------------------|---------------------------------------------------|
| Setup e ambiente                | [docs/setup.md](docs/setup.md)                   |
| Autenticação e cadastro         | [docs/accounts.md](docs/accounts.md)             |
| Perfil do usuário               | [docs/profile.md](docs/profile.md)               |
| Catálogo de destinos            | [docs/destinations.md](docs/destinations.md)     |
| Autocomplete de destinos        | [docs/autocomplete.md](docs/autocomplete.md)     |
| Destinos em destaque            | [docs/featured.md](docs/featured.md)             |
| Landing page                    | [docs/landing.md](docs/landing.md)               |
| Interface e design system       | [docs/design.md](docs/design.md)                 |
| Busca de imagens (Unsplash)     | [docs/image_search.md](docs/image_search.md)     |
| Testes                          | [docs/tests.md](docs/tests.md)                   |
| Roadmap                         | [docs/roadmap.md](docs/roadmap.md)               |

---

## Setup rápido

```bash
# Clone o repositório
git clone git@github.com:jonassonjp/plan-n-go.git ~/workspace/plan-n-go
cd ~/workspace/plan-n-go

# Execute o script de setup
chmod +x setup_plango.sh
./setup_plango.sh
```

Ou manualmente:

```bash
pyenv virtualenv 3.13.7 plan-n-go-venv
pyenv local plan-n-go-venv
pip install -r requirements-dev.txt
cp .env.example .env  # edite com suas chaves
python manage.py migrate
python manage.py runserver
```

---

## Variáveis de ambiente

Copie `.env.example` para `.env` e preencha:

```bash
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco (opcional — dev usa SQLite)
# DATABASE_URL=postgresql://usuario:senha@localhost:5432/plango

# E-mail (dev: imprime no terminal)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@plango.app

# IA — obtenha em console.anthropic.com
ANTHROPIC_API_KEY=

# Geocoding (nominatim = gratuito, google = requer chave)
GEOCODING_BACKEND=nominatim
GOOGLE_PLACES_API_KEY=

# CORS
FRONTEND_URL=http://localhost:5173
```

---

## Testes

```bash
# Todos os testes
pytest

# App específico
pytest accounts/tests/ -v

# Com relatório de cobertura
pytest --cov=. --cov-report=html
```

---

## Licença

MIT
