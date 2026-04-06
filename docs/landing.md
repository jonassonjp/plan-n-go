# Landing Page

## Visão geral

Página inicial pública do Plan N'Go (`/`).  
Não requer autenticação.

---

## Seções

### 1. Navbar
- Logo Plan N'Go
- Para visitantes: links "Entrar" e "Cadastrar"
- Para usuários logados: "Meu Dashboard" e "Sair"

### 2. Hero
- Foto de fundo (`static/img/hero-travel.jpg`)
- Título, subtítulo e tagline
- Botões "Começar Agora" e "Já tenho conta" / "Meu Dashboard"
- Wave decorativa na transição para o conteúdo

### 3. Destinos em Destaque
- Cards Polaroid clicáveis → página de detalhes do destino
- Carrossel com 4 por vez (se tiver mais de 4)
- Botão "+ Novo Destino" **removido** (usuário acessa pelo dashboard)

### 4. Features
6 cards explicando as funcionalidades:
- Autocompletar Inteligente
- Vistos e Vacinas
- Import do Instagram
- Itinerários Personalizados
- Colaboração
- Catálogo Visual

### 5. Footer
- Logo e descrição
- Links: Recursos e Suporte
- Redes sociais: Instagram, Twitter, GitHub

---

## Arquivos

| Arquivo                                    | Descrição                    |
|--------------------------------------------|------------------------------|
| `templates/plango/index.html`              | Template principal           |
| `static/css/landing.css`                   | CSS da landing page          |
| `plango/views.py`                          | View com destinos em destaque|
| `static/img/hero-travel.jpg`               | Foto do hero                 |
| `static/img/places/*.jpg`                  | Fotos dos cards mock         |
