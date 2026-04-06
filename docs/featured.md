# Destinos em Destaque

## Visão geral

Destinos criados pelo superusuário, exibidos publicamente na landing page como cards de exemplo.  
Qualquer visitante pode ver os detalhes sem precisar ter conta.

---

## Como criar destinos em destaque

1. Acesse `http://localhost:8000/admin`
2. Faça login com o superusuário
3. Clique em **Destinos em Destaque** → **Adicionar**
4. Preencha os campos (o campo `slug` é preenchido automaticamente pelo nome)
5. Marque **Ativo** e defina a **Ordem de exibição**
6. Salve

---

## URLs públicas

| URL                              | Descrição                                |
|----------------------------------|------------------------------------------|
| `/`                              | Landing page com carrossel de destinos   |
| `/feed/destino/<slug>/`          | Página de detalhes do destino            |

---

## Model FeaturedDestination

Localização: `feed/models.py`

### Campos principais

| Campo         | Descrição                                          |
|---------------|----------------------------------------------------|
| `name`        | Nome do destino                                    |
| `country`     | País                                               |
| `continent`   | Continente                                         |
| `slug`        | URL amigável (auto-gerado pelo admin)              |
| `description` | Texto editorial escrito pelo superusuário          |
| `photo_upload`| Upload de foto (prioridade)                        |
| `photo_url`   | URL externa de foto                                |
| `languages`   | Idiomas (JSON)                                     |
| `currency`    | Moeda                                              |
| `best_months` | Meses recomendados (JSON)                          |
| `is_active`   | Se aparece na landing page                         |
| `order`       | Ordem de exibição (menor = primeiro)               |

Exigências de entrada (mesmos campos do `Destination`):
`visa_required`, `visa_type`, `vaccination_required`, `vaccines`, `vaccines_notes`,
`other_requirements_title`, `other_requirements_description`

---

## Carrossel na landing page

- Exibe **4 cards por vez**
- Se houver mais de 4 destinos: aparece botões ← → e dots de navegação
- Animação suave com `transform: translateX`
- Se não houver destinos cadastrados: exibe 4 cards estáticos de exemplo (Machu Picchu, Tóquio, Santorini, Bali)

---

## Página de detalhes

URL: `/feed/destino/<slug>/`

Exibe:
- **Hero** com foto grande, título, país e continente
- **Descrição** editorial (se preenchida)
- **Cards de informações**:
  - Melhores meses para visitar
  - Idiomas falados
  - Moeda local
  - Visto (necessário / não necessário / verificar)
  - Vacinas (lista + observações)
  - Outras exigências (ex: ETIAS)
- **CTA** no rodapé:
  - Para usuários logados: "Adicionar à minha lista"
  - Para visitantes: "Criar conta e salvar este destino"
