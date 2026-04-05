#!/usr/bin/env bash
# =============================================================================
# Plan'Go — Setup do Ambiente de Desenvolvimento
# Python 3.13 + Django 6.0 + SQLite (dev) / PostgreSQL (prod)
#
# Estrutura de pastas:
#   Código do projeto → ~/workspace/plan-n-go/
#   Ambiente virtual  → ~/.pyenv/versions/plan-n-go-venv/
#
# PRÉ-REQUISITO: Crie o repositório manualmente em https://github.com/new
#   Nome:         plan-n-go
#   Conta:        jonassonjp
#   Visibilidade: Public
#   NÃO inicialize com README, .gitignore ou licença (o script faz isso)
# =============================================================================

set -e  # Aborta se qualquer comando falhar

echo ""
echo "🌍 Plan'Go — Configurando ambiente de desenvolvimento..."
echo "============================================================"

# -----------------------------------------------------------------------------
# Caminhos fixos do projeto
# -----------------------------------------------------------------------------
PROJECT_DIR="$HOME/workspace/plan-n-go"
VENV_NAME="plan-n-go-venv"
VENV_DIR="$HOME/.pyenv/versions/$VENV_NAME"

# -----------------------------------------------------------------------------
# 1. Inicializar pyenv
# -----------------------------------------------------------------------------
export PYENV_ROOT="${PYENV_ROOT:-$HOME/.pyenv}"
export PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"

if command -v pyenv &>/dev/null; then
  eval "$(pyenv init -)"
  eval "$(pyenv init --path)" 2>/dev/null || true
  eval "$(pyenv virtualenv-init -)" 2>/dev/null || true
else
  echo "  ✗ pyenv não encontrado."
  echo "  Instale via: https://github.com/pyenv/pyenv"
  exit 1
fi

# -----------------------------------------------------------------------------
# 2. Verificar Python 3.13+ no pyenv
# -----------------------------------------------------------------------------
echo ""
echo "▶ Verificando Python 3.13 no pyenv..."

PYENV_313=$(pyenv versions --bare | grep -E "^3\.13\." | sort -V | tail -1 || true)

if [ -z "$PYENV_313" ]; then
  echo "  ✗ Python 3.13.x não encontrado no pyenv."
  echo "  Instale com: pyenv install 3.13.7"
  exit 1
fi

echo "  ✓ Python $PYENV_313 disponível no pyenv."

# -----------------------------------------------------------------------------
# 3. Criar ambiente virtual no pyenv
# -----------------------------------------------------------------------------
echo ""
echo "▶ Criando ambiente virtual em $VENV_DIR ..."

if [ -d "$VENV_DIR" ]; then
  echo "  ⚠ Ambiente virtual '$VENV_NAME' já existe. Pulando criação."
else
  pyenv virtualenv "$PYENV_313" "$VENV_NAME"
  echo "  ✓ Ambiente virtual '$VENV_NAME' criado."
fi

# Ativar o ambiente virtual
pyenv activate "$VENV_NAME"
echo "  ✓ Ambiente virtual '$VENV_NAME' ativado."
echo "  ✓ Python: $(python --version)"

# -----------------------------------------------------------------------------
# 4. Atualizar pip
# -----------------------------------------------------------------------------
echo ""
echo "▶ Atualizando pip..."
pip install --upgrade pip --quiet
echo "  ✓ pip atualizado: $(pip --version)"

# -----------------------------------------------------------------------------
# 5. Instalar dependências de produção
# -----------------------------------------------------------------------------
echo ""
echo "▶ Instalando dependências de produção..."

pip install --quiet \
  django==6.0.3 \
  djangorestframework==3.15.2 \
  django-cors-headers==4.6.0 \
  djangorestframework-simplejwt==5.4.0 \
  pillow==11.1.0 \
  python-dotenv==1.0.1 \
  requests==2.32.3 \
  beautifulsoup4==4.12.3 \
  anthropic==0.49.0 \
  psycopg2-binary==2.9.10 \
  whitenoise==6.9.0

echo "  ✓ Dependências de produção instaladas."

# -----------------------------------------------------------------------------
# 6. Instalar dependências de desenvolvimento e testes
# -----------------------------------------------------------------------------
echo ""
echo "▶ Instalando dependências de desenvolvimento e testes..."

pip install --quiet \
  pytest==8.3.5 \
  pytest-django==4.9.0 \
  pytest-cov==6.0.0 \
  factory-boy==3.3.1 \
  faker==33.1.0 \
  black==24.10.0 \
  flake8==7.1.1 \
  isort==5.13.2

echo "  ✓ Dependências de dev/teste instaladas."

# -----------------------------------------------------------------------------
# 7. Criar pasta do projeto e entrar nela
# -----------------------------------------------------------------------------
echo ""
echo "▶ Preparando pasta do projeto em $PROJECT_DIR ..."

mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
echo "  ✓ Pasta criada e diretório atual: $(pwd)"

# Vincular o venv a esta pasta via pyenv local
pyenv local "$VENV_NAME"
echo "  ✓ pyenv local configurado para '$VENV_NAME' nesta pasta."

# -----------------------------------------------------------------------------
# 8. Gerar requirements
# -----------------------------------------------------------------------------
echo ""
echo "▶ Gerando arquivos de requirements..."

pip freeze | grep -v -E "pytest|factory|faker|black|flake8|isort|coverage" > requirements.txt
pip freeze > requirements-dev.txt

echo "  ✓ requirements.txt gerado (produção)."
echo "  ✓ requirements-dev.txt gerado (desenvolvimento)."

# -----------------------------------------------------------------------------
# 9. Criar projeto Django e apps
# -----------------------------------------------------------------------------
echo ""
echo "▶ Criando projeto Django..."

if [ -f "manage.py" ]; then
  echo "  ⚠ Projeto Django já existe. Pulando criação."
else
  django-admin startproject plango .
  echo "  ✓ Projeto 'plango' criado."
fi

echo ""
echo "▶ Criando apps..."

APPS=("accounts" "destinations" "lists" "itineraries" "feed")

for APP in "${APPS[@]}"; do
  if [ -d "$APP" ]; then
    echo "  ⚠ App '$APP' já existe. Pulando."
  else
    python manage.py startapp "$APP"
    echo "  ✓ App '$APP' criado."
  fi
done

# -----------------------------------------------------------------------------
# 10. Criar arquivos de configuração
# -----------------------------------------------------------------------------
echo ""
echo "▶ Criando arquivos de configuração..."

# .env
if [ -f ".env" ]; then
  echo "  ⚠ .env já existe. Pulando."
else
  cat > .env <<'EOF'
# =============================================================
# Plan'Go — Variáveis de Ambiente
# NUNCA commite este arquivo no git!
# =============================================================

# Django
SECRET_KEY=django-insecure-troque-esta-chave-em-producao
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de dados
# Dev usa SQLite automaticamente quando DATABASE_URL não está definido
# Para PostgreSQL em produção, descomente e configure:
# DATABASE_URL=postgresql://usuario:senha@localhost:5432/plango

# E-mail (dev usa console, não envia e-mails reais)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@plango.app

# Anthropic (Claude API) — obtenha em console.anthropic.com
ANTHROPIC_API_KEY=sua-chave-aqui

# Frontend (CORS)
FRONTEND_URL=http://localhost:5173
EOF
  echo "  ✓ .env criado."
fi

# .env.example
cat > .env.example <<'EOF'
# =============================================================
# Plan'Go — Variáveis de Ambiente (exemplo)
# Copie para .env e preencha com seus valores reais
# =============================================================

SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# DATABASE_URL=postgresql://usuario:senha@localhost:5432/plango

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@plango.app

ANTHROPIC_API_KEY=

FRONTEND_URL=http://localhost:5173
EOF
echo "  ✓ .env.example criado."

# .gitignore
if [ -f ".gitignore" ]; then
  echo "  ⚠ .gitignore já existe. Pulando."
else
  cat > .gitignore <<'EOF'
# Ambiente virtual (gerenciado pelo pyenv, fora do projeto)
.venv/
venv/
env/

# Django
*.pyc
__pycache__/
db.sqlite3
media/
staticfiles/

# Variáveis de ambiente
.env
.env.*
!.env.example

# Testes
.coverage
htmlcov/
.pytest_cache/

# pyenv
.python-version

# IDEs
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
EOF
  echo "  ✓ .gitignore criado."
fi

# pytest.ini
if [ -f "pytest.ini" ]; then
  echo "  ⚠ pytest.ini já existe. Pulando."
else
  cat > pytest.ini <<'EOF'
[pytest]
DJANGO_SETTINGS_MODULE = plango.settings
python_files = tests/*.py tests/**/*.py
addopts = --cov=. --cov-report=term-missing --cov-report=html -v
EOF
  echo "  ✓ pytest.ini criado."
fi

# README.md
if [ -f "README.md" ]; then
  echo "  ⚠ README.md já existe. Pulando."
else
  cat > README.md <<'EOF'
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
EOF
  echo "  ✓ README.md criado."
fi

# -----------------------------------------------------------------------------
# 11. Inicializar repositório Git e push
# -----------------------------------------------------------------------------
echo ""
echo "▶ Verificando git..."

if ! command -v git &>/dev/null; then
  echo "  ✗ git não encontrado."
  exit 1
fi

if ! git config --global user.email &>/dev/null; then
  echo "  ✗ Identidade Git não configurada. Execute:"
  echo "    git config --global user.name  \"Seu Nome\""
  echo "    git config --global user.email \"seu@email.com\""
  exit 1
fi
echo "  ✓ git: $(git config --global user.name) <$(git config --global user.email)>"

echo ""
echo "▶ Inicializando repositório Git local..."

if [ -d ".git" ]; then
  echo "  ⚠ Repositório Git já existe. Pulando init."
else
  git init
  git branch -M main
  echo "  ✓ Repositório Git inicializado na branch main."
fi

echo ""
echo "▶ Configurando remote origin..."

GITHUB_SSH="git@github.com:jonassonjp/plan-n-go.git"

if git remote get-url origin &>/dev/null; then
  echo "  ⚠ Remote 'origin' já configurado: $(git remote get-url origin)"
else
  git remote add origin "$GITHUB_SSH"
  echo "  ✓ Remote origin: $GITHUB_SSH"
fi

# -----------------------------------------------------------------------------
# 12. Commit e push inicial
# -----------------------------------------------------------------------------
echo ""
echo "▶ Realizando commit e push inicial..."

git add .

git commit -m "chore: setup inicial do projeto Plan N'Go

- Configuração do ambiente Python 3.13 + Django 6.0.3
- Apps criados: accounts, destinations, lists, itineraries, feed
- Dependências de produção e desenvolvimento configuradas
- Estrutura base do projeto com Django REST Framework
- Configuração de testes com pytest, pytest-django e pytest-cov
- Arquivos incluídos: .gitignore, .env.example, README.md, pytest.ini
- requirements.txt (produção) e requirements-dev.txt (desenvolvimento)

Stack:
  Backend  → Python 3.13 / Django 6.0.3 / Django REST Framework
  Banco    → SQLite (dev) / PostgreSQL (produção)
  IA       → Anthropic Claude API (importação de destinos por URL)
  Frontend → React + TypeScript + Tailwind CSS (repositório separado)"

git push -u origin main

echo "  ✓ Push inicial realizado com sucesso!"

# -----------------------------------------------------------------------------
# 13. Resumo final
# -----------------------------------------------------------------------------
echo ""
echo "============================================================"
echo "✅  Tudo pronto! Ambiente configurado e código no GitHub."
echo "============================================================"
echo ""
echo "  Python:          $(python --version)"
echo "  Django:          $(python -m django --version)"
echo "  Projeto:         $PROJECT_DIR"
echo "  Ambiente virtual: $VENV_DIR"
echo "  Repositório:     https://github.com/jonassonjp/plan-n-go"
echo ""
echo "  Apps criados:"
for APP in "${APPS[@]}"; do
  echo "    • $APP"
done
echo ""
echo "  Próximos passos:"
echo "    1. Edite .env → preencha SECRET_KEY e ANTHROPIC_API_KEY"
echo "    2. Edite plango/settings.py → adicione os apps em INSTALLED_APPS"
echo "    3. python manage.py migrate"
echo "    4. python manage.py runserver"
echo ""
echo "  O pyenv ativa o venv automaticamente ao entrar na pasta."
echo "  Mas se precisar ativar manualmente:"
echo "    pyenv activate plan-n-go-venv"
echo ""
echo "  Para rodar os testes:"
echo "    pytest"
echo ""
