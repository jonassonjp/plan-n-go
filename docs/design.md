# Interface e Design System

## Paleta de cores

| Token                  | Valor HSL              | Uso                          |
|------------------------|------------------------|------------------------------|
| `--color-primary`      | `hsl(16, 85%, 58%)`    | Coral/Terracota — cor principal |
| `--color-primary-hover`| `hsl(16, 85%, 50%)`    | Hover dos botões             |
| `--color-secondary`    | `hsl(35, 30%, 92%)`    | Fundo secundário, creme      |
| `--color-bg`           | `hsl(35, 33%, 97%)`    | Fundo da página              |
| `--color-fg`           | `hsl(20, 20%, 15%)`    | Texto principal              |
| `--color-muted-fg`     | `hsl(20, 10%, 45%)`    | Texto secundário             |
| `--color-accent`       | `hsl(174, 60%, 40%)`   | Teal — badges de meses       |
| `--color-border`       | `hsl(35, 20%, 88%)`    | Bordas                       |
| `--color-footer-bg`    | `hsl(25, 35%, 35%)`    | Marrom quente do footer      |

---

## Tipografia

| Variável              | Fonte                | Uso                          |
|-----------------------|----------------------|------------------------------|
| `--font-display`      | Playfair Display     | Títulos, logo                |
| `--font-body`         | DM Sans              | Texto geral, formulários     |
| `--font-handwritten`  | Caveat               | Elementos decorativos        |

---

## Arquivos CSS

| Arquivo                           | Escopo                                |
|-----------------------------------|---------------------------------------|
| `static/css/plango.css`           | Design system base (tokens globais)   |
| `static/css/landing.css`          | Landing page                          |
| `static/css/auth.css`             | Login, cadastro, perfil               |
| `static/css/app.css`              | Navbar interna, layout do sistema     |
| `static/css/dashboard.css`        | Dashboard, cards Polaroid, modal      |
| `static/css/autocomplete.css`     | Dropdown de autocomplete              |
| `static/css/destination_detail.css` | Página de detalhes e carrossel      |

---

## Componentes principais

### Card Polaroid
```
.polaroid-card         → container com sombra e rotação sutil
.polaroid-card__tape   → fita decorativa amarela no topo
.polaroid-card__photo  → área da foto (aspect-ratio 4/3)
.polaroid-card__label  → área branca inferior com nome e metadados
.polaroid-card__icon-actions → ícones editar/excluir (aparecem no hover)
```

### Botões
```
.btn-primary    → coral, arredondado, com sombra
.btn-ghost      → transparente com borda
.btn--primary   → variante para landing page
.btn--outline   → branco semi-transparente (hero)
```

### Modal
```
.modal-backdrop           → overlay com blur
.modal-backdrop--open     → estado aberto (visibility + opacity)
.modal                    → container do modal
.modal-header / .modal-body / .modal-footer
```

### Tags e meses (formulários)
```
.tag-btn           → tag de idioma (clicável)
.tag-btn--active   → estado ativo (coral)
.month-btn         → botão de mês
.month-btn--active → estado ativo
```

---

## Templates Django

| Template                                     | Descrição                          |
|----------------------------------------------|------------------------------------|
| `templates/plango/base.html`                 | Base com fonts, CSS e JS globais   |
| `templates/plango/index.html`                | Landing page                       |
| `templates/components/app_navbar.html`       | Navbar das páginas internas        |
| `templates/components/footer.html`           | Footer                             |
| `templates/accounts/register.html`           | Cadastro                           |
| `templates/accounts/register_done.html`      | Aguardando confirmação de e-mail   |
| `templates/accounts/login.html`              | Login                              |
| `templates/accounts/profile_setup.html`      | Setup de perfil (pós-confirmação)  |
| `templates/destinations/dashboard.html`      | Dashboard de destinos              |
| `templates/destinations/place_card.html`     | Card Polaroid (componente)         |
| `templates/feed/destination_detail.html`     | Detalhes do destino em destaque    |

---

## JavaScript

| Arquivo                                      | Descrição                         |
|----------------------------------------------|-----------------------------------|
| `static/js/plango.js`                        | Utilitários gerais                |
| `static/js/destination_autocomplete.js`      | Autocomplete de destinos          |
