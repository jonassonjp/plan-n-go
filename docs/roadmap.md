# Roadmap

## ✅ Implementado

### Setup e infraestrutura
- [x] Ambiente Python 3.13 + Django 6.0 com pyenv
- [x] Script de setup automatizado (`setup_plango.sh`)
- [x] Repositório GitHub com commits convencionais
- [x] `settings.py` com SQLite (dev) e PostgreSQL (prod)
- [x] Variáveis de ambiente via `.env`

### Autenticação
- [x] Model `User` customizado (login por e-mail)
- [x] Backend de autenticação por e-mail (case-insensitive)
- [x] Cadastro com apenas nome, e-mail e senha
- [x] Confirmação de e-mail via token UUID
- [x] Login automático após confirmação
- [x] Página de perfil dentro do sistema (com navbar, indicador de progresso)
- [x] Campos de perfil: foto, nome público, nacionalidade
- [x] Redefinição de senha via e-mail (4 views, 5 templates)
- [x] Comandos de gerenciamento: `set_passwords_to_123`, `set_superuser`
- [x] Troca de e-mail com confirmação por token (fluxo seguro, e-mail atual ativo até confirmação)

### Destinos
- [x] Model `Destination` completo
- [x] Campos: nome, país, continente, idiomas, moeda, meses recomendados
- [x] Exigências de entrada: visto, vacinas (lista pré-definida), outras exigências
- [x] Upload de imagem ou URL externa
- [x] CRUD completo: criar, editar (modal), excluir
- [x] Cards Polaroid com ícones de editar/excluir no hover
- [x] Dashboard com grid responsivo

### Autocomplete
- [x] Backend Nominatim (gratuito, sem cadastro)
- [x] Backend Google Places (pronto, ativar via `.env`)
- [x] Preenchimento automático de país e continente
- [x] Preenchimento automático de idiomas por país (40+ países)
- [x] Debounce 400ms e navegação por teclado

### Landing page
- [x] Hero com foto, título e CTAs
- [x] Seção de features (6 cards)
- [x] Footer com links e redes sociais
- [x] Design system fiel ao original (coral/terracota, Playfair Display)

### Destinos em destaque
- [x] Model `FeaturedDestination` gerenciado pelo superusuário via admin
- [x] Carrossel na landing page (4 por vez, dots, prev/next)
- [x] Página de detalhes: `/feed/destino/<slug>/`
- [x] Informações: foto grande, meses, idiomas, moeda, visto, vacinas

### Importação por URL
- [x] Scraping de blogs e sites de viagem
- [x] Extração de dados via Gemini 2.5 Flash (gratuito, padrão)
- [x] Extração via Anthropic Claude (alternativa para produção)
- [x] Opção de colar texto manualmente (ideal para Instagram)
- [x] Busca automática de imagem via Unsplash API
- [x] Alternativa documentada: Google Custom Search API

### Listas
- [x] Listas manuais de destinos
- [x] Listas inteligentes com critérios (por continente, país, idioma, mês)
- [x] Um destino pode estar em várias listas
- [x] Toggle via AJAX no dashboard de destinos

### Testes
- [x] 28 testes no app `accounts` (cobertura ~92%)
- [x] 12 testes no app `destinations` (geocoding)
- [x] 17 testes no app `lists`
- [x] 9 testes de aceitação E2E com Playwright (auth + lists)
- [x] Integração com pytest-cov

---

### Roteiros
- [x] Model `Roteiro` vinculado a um destino do usuário
- [x] Model `Dia` — cada roteiro tem N dias
- [x] Model `Indicacao` — cada dia tem N indicações (pontos turísticos, atividades)
- [x] Custo médio de hospedagem e alimentação por dia
- [x] Geração automática via IA (Claude Sonnet)
- [x] Edição manual dia a dia
- [x] Visibilidade: privado, restrito, público
- [x] Loading spinner durante geração com IA

### Feed público
- [x] Exploração de destinos e roteiros públicos de outros usuários
- [x] Feed de descoberta

---

## 🚧 Em desenvolvimento

### Avaliação pós-visita
- [ ] 1 a 5 estrelas [#12](https://github.com/jonassonjp/plan-n-go/issues/12)
- [ ] "Voltaria novamente?" [#13](https://github.com/jonassonjp/plan-n-go/issues/13)
- [ ] Texto livre e fotos [#14](https://github.com/jonassonjp/plan-n-go/issues/14)

### Confirmação de e-mail (produção)
- [ ] Integração com provedor real (SendGrid, Mailgun, etc.) [#15](https://github.com/jonassonjp/plan-n-go/issues/15)
- [ ] Reenvio de e-mail de confirmação [#16](https://github.com/jonassonjp/plan-n-go/issues/16)

---

## 💡 Futuro

- [ ] Página de detalhes do destino do usuário (atualmente só existe para destinos em destaque do superusuário — criar versão para destinos do catálogo pessoal) [#17](https://github.com/jonassonjp/plan-n-go/issues/17)
- [ ] App mobile (iOS e Android) [#18](https://github.com/jonassonjp/plan-n-go/issues/18)
- [ ] Integração com Google Maps (mapa dos destinos) [#19](https://github.com/jonassonjp/plan-n-go/issues/19)
- [ ] Notificações de melhores épocas para visitar [#20](https://github.com/jonassonjp/plan-n-go/issues/20)
- [ ] Importação em lote de destinos [#21](https://github.com/jonassonjp/plan-n-go/issues/21)
