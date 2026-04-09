# Workflow de Desenvolvimento

## Fluxo por funcionalidade

Cada nova funcionalidade segue este fluxo obrigatório:

```
main (estável)
  │
  └─► feature/<nome>      ← desenvolvimento aqui
        │
        ├─ commits convencionais
        ├─ testes unitários passando
        ├─ testes de aceitação passando
        │
        └─► PR → main     ← CI bloqueia merge se falhar
```

---

## Convenção de nomes de branch

| Tipo | Padrão | Exemplo |
|---|---|---|
| Nova feature | `feature/<nome>` | `feature/lists` |
| Correção de bug | `fix/<nome>` | `fix/login-redirect` |
| Hotfix em produção | `hotfix/<nome>` | `hotfix/csrf-token` |
| Refatoração | `refactor/<nome>` | `refactor/geocoding` |

---

## Comandos Git para cada funcionalidade

### 1. Atualizar main e criar nova branch

```bash
git checkout main
git pull origin main
git checkout -b feature/<nome-da-feature>
```

### 2. Desenvolver e fazer commits

```bash
git add <arquivos>
git commit -m "feat(<escopo>): <descrição curta>"

# Tipos de commit:
# feat     → nova funcionalidade
# fix      → correção de bug
# test     → adição/ajuste de testes
# docs     → documentação
# refactor → refatoração sem mudança de comportamento
# chore    → tarefas de manutenção (deps, config)
```

### 3. Antes do merge — rodar todos os testes

```bash
# Testes unitários
python -m pytest --no-cov -v

# Testes de aceitação E2E (requer servidor rodando)
python manage.py runserver &
python -m pytest tests/acceptance/ -v

# Se tudo passar:
git push origin feature/<nome-da-feature>
```

### 4. Abrir Pull Request no GitHub

```
GitHub → Compare & pull request
  Base: main  ←  Compare: feature/<nome>
  Título: feat(<escopo>): descrição
```

O CI roda automaticamente:
- ✅ Testes unitários (pytest)
- ✅ Lint (ruff)
- ✅ Testes de aceitação Playwright

### 5. Fazer o merge (após CI verde)

```bash
# Via GitHub: botão "Squash and merge" no PR (recomendado)

# Ou via linha de comando:
git checkout main
git pull origin main
git merge --no-ff feature/<nome> -m "feat(<escopo>): <descrição>"
git push origin main

# Limpar branches
git branch -d feature/<nome>
git push origin --delete feature/<nome>
```

---

## Rodando os testes de aceitação localmente

```bash
# Instalar Playwright (primeira vez)
pip install pytest-playwright
playwright install chromium

# Terminal 1 — servidor Django
python manage.py runserver

# Terminal 2 — testes E2E
python -m pytest tests/acceptance/ -v

# Com browser visível (debug)
python -m pytest tests/acceptance/ -v --headed

# Arquivo específico
python -m pytest tests/acceptance/test_lists.py -v
```

---

## GitHub Actions

### `ci.yml` — roda em todo push para main/feature/fix

- Instala dependências, migra banco, roda pytest, faz lint com ruff
- Salva relatório de cobertura como artefato

### `acceptance.yml` — roda em PRs para main

- Instala Playwright + Chromium, sobe Django, roda testes E2E
- Salva screenshots e vídeos de falhas como artefato
- Pode ser acionado manualmente via `workflow_dispatch`

### Proteger a branch main

```
GitHub → Settings → Branches → Add branch protection rule
  Branch name pattern: main
  ✅ Require a pull request before merging
  ✅ Require status checks to pass:
       - "Testes unitários e integração"
       - "Playwright E2E"
  ✅ Require branches to be up to date before merging
  ✅ Do not allow bypassing the above settings
```

---

## Estado das branches

```
main           → código estável
feature/lists  → módulo de listas (41 testes passando)
```

### Mergear feature/lists

```bash
git checkout main
git pull origin main
git merge --no-ff feature/lists -m "feat(lists): implementar módulo de listas de destinos"
git push origin main
git branch -d feature/lists
git push origin --delete feature/lists
```
