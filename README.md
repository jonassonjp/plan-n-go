# Plan N'Go 🌍

Catalogue seus destinos dos sonhos, planeje roteiros com IA e compartilhe suas viagens.

## Stack

- **Backend:** Python 3.13 + Django 6.0 + Django REST Framework
- **Banco:** SQLite (dev) / PostgreSQL (produção)
- **IA:** Claude (Anthropic API) — importação de destinos por URL
- **Frontend:** React + TypeScript + Tailwind CSS

## Apps

| App | Responsabilidade |
|-----|-----------------|
| `accounts` | Cadastro, autenticação e perfis de usuário |
| `destinations` | Catálogo de destinos de viagem |
| `lists` | Listas manuais e listas inteligentes |
| `itineraries` | Roteiros com IA e colaboração em tempo real |
| `feed` | Exploração pública de destinos e roteiros |

## Setup

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

## Testes

```bash
pytest
```

## Licença

MIT
