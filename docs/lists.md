# Listas de Destinos

## Visão geral

O módulo `lists` permite ao usuário organizar seus destinos em listas temáticas de dois tipos:

| Tipo | Comportamento |
|---|---|
| **Manual** | O usuário escolhe explicitamente quais destinos entram na lista |
| **Inteligente** | Destinos são filtrados automaticamente por critérios (continente, país, idioma, meses) |

Um mesmo destino pode pertencer a várias listas.

---

## Models

### `DestinationList`

| Campo | Tipo | Descrição |
|---|---|---|
| `user` | FK → User | Dono da lista |
| `name` | CharField | Nome da lista (max 200 chars) |
| `emoji` | CharField | Emoji decorativo (padrão `📍`) |
| `description` | TextField | Descrição opcional |
| `slug` | SlugField | Gerado automaticamente |
| `list_type` | CharField | `manual` ou `smart` |
| `smart_criteria` | JSONField | Critérios para listas inteligentes |
| `destinations` | M2M | Via `ListItem` (ordenação preservada) |
| `visibility` | CharField | `private`, `restricted`, `public` |

**`smart_criteria` — formato:**
```json
{
  "continents": ["Europa", "Ásia"],
  "countries":  ["Japão", "França"],
  "languages":  ["Japonês", "Inglês"],
  "months":     [3, 4, 11]
}
```
Campos ausentes ou vazios são ignorados (sem restrição).

**Método `get_destinations()`** — resolve os destinos:
- Manual → `ListItem` ordenados por `position`
- Inteligente → queryset filtrado pelos critérios

### `ListItem`

Tabela intermediária M2M com campo `position` (inteiro) para preservar a ordem de inserção do usuário. A constraint `unique_together` garante que o mesmo destino não apareça duas vezes na mesma lista.

---

## URLs

| URL | Nome | Descrição |
|---|---|---|
| `GET /lists/` | `lists:dashboard` | Dashboard com todas as listas |
| `POST /lists/nova/` | `lists:create` | Criar nova lista |
| `GET /lists/<pk>/` | `lists:detail` | Detalhe e destinos da lista |
| `POST /lists/<pk>/editar/` | `lists:edit` | Editar nome/emoji/critérios |
| `POST /lists/<pk>/excluir/` | `lists:delete` | Excluir lista |
| `POST /lists/<pk>/adicionar/` | `lists:add_destination` | Adicionar destino (manual) |
| `POST /lists/<pk>/remover/<dest_pk>/` | `lists:remove_destination` | Remover destino (manual) |
| `GET /lists/api/destino/<dest_pk>/listas/` | `lists:api_lists_for_destination` | JSON: listas disponíveis |
| `POST /lists/api/<pk>/toggle/` | `lists:api_toggle` | JSON: toggle destino na lista |

---

## Templates

| Template | Descrição |
|---|---|
| `templates/lists/dashboard.html` | Grid de cards de listas + modal "Nova Lista" |
| `templates/lists/detail.html` | Destinos da lista + modais Editar e Adicionar |

### Modal "Nova Lista"
- Toggle **Manual / Inteligente** atualiza a dica e mostra/oculta os critérios
- Emoji picker com 18 opções
- Critérios inteligentes: chips de seleção múltipla para continentes, idiomas e meses; campo texto livre para países

---

## CSS

Arquivo: `static/css/lists.css`

Classes principais:

```
.lists-grid              → Grid responsivo de cards (1→2→3→4 colunas)
.list-card               → Card de lista com hover sutil
.list-card--new          → Card "Nova Lista" com borda tracejada
.list-card__badge--smart → Badge teal para listas inteligentes
.list-card__badge--manual → Badge coral para listas manuais
.list-card__photos       → Preview de 3 thumbs + contador
.list-detail-header      → Cabeçalho da página de detalhe
.list-smart-criteria     → Pills com os critérios ativos
.list-type-toggle        → Toggle Manual/Inteligente no modal
.chip / .chip-group      → Seleção múltipla de critérios
.emoji-btn / .emoji-picker → Picker de emoji
.modal-overlay / .modal-box → Sistema de modais com animação
```

---

## Navbar

O link **Minhas Listas** foi adicionado à navbar interna (`templates/components/app_navbar.html`) ao lado de "Meus Destinos".

---

## Testes

41 testes em `lists/tests.py`, organizados em 8 classes:

| Classe | Testes |
|---|---|
| `TestDestinationListModel` | 11 — models e método `get_destinations()` |
| `TestListItemModel` | 3 — criação, unicidade, `__str__` |
| `TestListsDashboard` | 4 — acesso, isolamento por usuário |
| `TestListCreate` | 5 — criação manual/inteligente, validações |
| `TestListDetail` | 4 — acesso, exibição, isolamento |
| `TestListEdit` | 2 — edição, proteção de dono |
| `TestListDelete` | 2 — exclusão, proteção de dono |
| `TestListManageDestinations` | 4 — add/remove, posição, segurança |
| `TestApiListsForDestination` | 4 — JSON, `has_destination`, filtro por tipo |
| `TestApiToggleDestination` | 2 — toggle add/remove |

```bash
python -m pytest lists/tests.py -v --no-cov
# 41 passed
```
