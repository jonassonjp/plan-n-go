# Catálogo de Destinos

## Visão geral

Cada usuário tem seu próprio catálogo de destinos de viagem.  
Os destinos são exibidos em cards estilo Polaroid no dashboard.

---

## URLs

| URL                           | Método | Descrição                          |
|-------------------------------|--------|------------------------------------|
| `/destinations/`              | GET    | Dashboard com grid de destinos     |
| `/destinations/create/`       | POST   | Criar novo destino                 |
| `/destinations/<pk>/update/`  | POST   | Atualizar destino existente        |
| `/destinations/<pk>/delete/`  | POST   | Remover destino                    |
| `/destinations/<pk>/edit-data/` | GET  | Dados do destino em JSON (AJAX)    |

---

## Model Destination

Localização: `destinations/models.py`

### Campos de identificação

| Campo       | Descrição                              |
|-------------|----------------------------------------|
| `name`      | Nome do destino                        |
| `country`   | País                                   |
| `continent` | Detectado automaticamente              |
| `city`      | Cidade (opcional)                      |
| `languages` | Lista de idiomas (JSON)                |

### Informações práticas

| Campo        | Descrição                          |
|--------------|------------------------------------|
| `currency`   | Moeda (ex: BRL, USD, EUR)          |
| `best_months`| Lista de meses ideais (JSON, 1-12) |

### Imagem

| Campo          | Descrição                                         |
|----------------|---------------------------------------------------|
| `photo_upload` | Upload direto de arquivo (prioridade)             |
| `photo_url`    | URL externa de imagem                             |
| `photo`        | Property: retorna upload ou URL (upload prevalece)|

### Exigências de entrada

| Campo                             | Descrição                              |
|-----------------------------------|----------------------------------------|
| `visa_required`                   | Boolean (null = não sei)               |
| `visa_type`                       | Tipo de visto (ex: E-visa)             |
| `vaccination_required`            | Boolean (null = não sei)               |
| `vaccines`                        | Lista de vacinas necessárias (JSON)    |
| `vaccines_notes`                  | Observações sobre vacinas              |
| `other_requirements_title`        | Ex: ETIAS                              |
| `other_requirements_description`  | Descrição da exigência                 |

### Vacinas disponíveis

```
febre_amarela, covid, hepatite_a, hepatite_b, tifoide,
colera, meningite, raiva, encefalite, poliomielite, outra
```

### Visibilidade e status

| Campo        | Opções                              |
|--------------|-------------------------------------|
| `visibility` | `private`, `restricted`, `public`   |
| `status`     | `draft` (importado), `active`       |

---

## Cards Polaroid

Cada destino é exibido como um card Polaroid com:

- **Fita** decorativa amarela no topo
- **Foto** (upload, URL ou placeholder)
- **Badges** na foto: meses recomendados e visto (se necessário)
- **Label** inferior: nome, país, idioma principal, moeda
- **Ícones** de editar (lápis) e excluir (lixeira) no canto superior direito ao hover

---

## Modal de criação/edição

Um único modal é usado para criar e editar destinos.

- **Criar**: abre vazio
- **Editar**: busca os dados via AJAX em `/destinations/<pk>/edit-data/` e preenche todos os campos
- Idiomas e meses: botões de toggle clicáveis
- Vacinas: aparecem apenas quando "Sim, precisa" selecionado
- Imagem: tabs "Fazer upload" e "Inserir URL" com preview imediato
