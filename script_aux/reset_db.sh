#!/usr/bin/env bash
# =============================================================================
# Plan'Go — Reset do banco de dados e migrate limpo
# =============================================================================

set -e

PROJECT_DIR="$HOME/workspace/plan-n-go"

echo ""
echo "🌍 Plan'Go — Resetando banco e rodando migrate..."
echo "============================================================"

# Ativar pyenv venv
export PYENV_ROOT="${PYENV_ROOT:-$HOME/.pyenv}"
export PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
eval "$(pyenv init -)" 2>/dev/null || true
eval "$(pyenv virtualenv-init -)" 2>/dev/null || true
pyenv activate plan-n-go-venv 2>/dev/null || true

cd "$PROJECT_DIR"

# Apagar banco SQLite antigo
echo ""
echo "▶ Removendo banco de dados antigo..."
if [ -f "db.sqlite3" ]; then
  rm db.sqlite3
  echo "  ✓ db.sqlite3 removido."
else
  echo "  ⚠ db.sqlite3 não encontrado. Pulando."
fi

# Apagar migrations antigas de todos os apps do projeto
# (mantém as migrations do Django, só remove as do nosso código)
echo ""
echo "▶ Removendo migrations antigas dos apps..."
for APP in accounts destinations lists itineraries feed; do
  MIGRATIONS_DIR="$PROJECT_DIR/$APP/migrations"
  if [ -d "$MIGRATIONS_DIR" ]; then
    find "$MIGRATIONS_DIR" -name "*.py" ! -name "__init__.py" -delete
    echo "  ✓ $APP/migrations/ limpo."
  fi
done

# Recriar migrations de todos os apps
echo ""
echo "▶ Recriando migrations..."
python manage.py makemigrations accounts destinations lists itineraries feed
echo "  ✓ Migrations recriadas."

# Rodar migrate limpo
echo ""
echo "▶ Rodando migrate..."
python manage.py migrate
echo "  ✓ Banco criado do zero com sucesso."

echo ""
echo "============================================================"
echo "✅  Banco de dados pronto!"
echo "============================================================"
echo ""
echo "  Criar superusuário (opcional):"
echo "    cd ~/workspace/plan-n-go"
echo "    python manage.py createsuperuser"
echo ""
echo "  Iniciar o servidor:"
echo "    python manage.py runserver"
echo ""
