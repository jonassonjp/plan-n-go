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

### Testes
- [x] 28 testes no app `accounts` (cobertura ~92%)
- [x] 12 testes no app `destinations` (geocoding)
- [x] Integração com pytest-cov

---

## 🚧 Em desenvolvimento

### Importação por URL
- [ ] Scraping de URLs (Instagram, blogs, TripAdvisor)
- [ ] Integração com Claude API para interpretar o conteúdo
- [ ] Destino salvo como rascunho para revisão do usuário

### Listas
- [ ] Listas manuais de destinos
- [ ] Listas inteligentes com critérios (por continente, país, idioma)
- [ ] Um destino pode estar em várias listas

### Roteiros
- [ ] Geração de roteiro por IA (Claude)
- [ ] Edição manual dia a dia
- [ ] Compartilhamento por convite com edição colaborativa
- [ ] Visibilidade: privado, restrito, público

### Feed público
- [ ] Exploração de destinos públicos de outros usuários
- [ ] Feed de descoberta

### Avaliação pós-visita
- [ ] 1 a 5 estrelas
- [ ] "Voltaria novamente?"
- [ ] Texto livre e fotos

### Confirmação de e-mail (produção)
- [ ] Integração com provedor real (SendGrid, Mailgun, etc.)
- [ ] Reenvio de e-mail de confirmação

---

## 💡 Futuro

- [ ] Página de detalhes do destino do usuário (atualmente só existe para destinos em destaque do superusuário — criar versão para destinos do catálogo pessoal)
- [ ] App mobile (iOS e Android)
- [ ] Integração com Google Maps (mapa dos destinos)
- [ ] Notificações de melhores épocas para visitar
- [ ] Importação em lote de destinos
