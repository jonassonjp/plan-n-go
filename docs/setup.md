# Setup e Ambiente

## Pré-requisitos

- Python 3.13+ (gerenciado via **pyenv**)
- git
- Conexão SSH configurada com o GitHub

---

## Estrutura de pastas

```
~/workspace/plan-n-go/      ← código do projeto
~/.pyenv/versions/plan-n-go-venv/  ← ambiente virtual
```

---

## Instalação

O script `setup_plango.sh` faz tudo automaticamente:

```bash
cd ~/workspace/plan-n-go
chmod +x setup_plango.sh
./setup_plango.sh
```

### O que o script faz

1. Verifica Python 3.13+ via pyenv
2. Cria o ambiente virtual `plan-n-go-venv` no pyenv
3. Instala dependências de produção e desenvolvimento
4. Cria o projeto Django e os 5 apps
5. Gera `.env`, `.gitignore`, `pytest.ini` e `README.md`
6. Inicializa o repositório git e faz o push inicial

---

## Dependências de produção

| Pacote                          | Versão   | Uso                              |
|---------------------------------|----------|----------------------------------|
| django                          | 6.0.3    | Framework principal              |
| djangorestframework             | 3.15.2   | API REST                         |
| django-cors-headers             | 4.6.0    | CORS para o frontend React       |
| djangorestframework-simplejwt   | 5.4.0    | Autenticação JWT                 |
| pillow                          | 11.1.0   | Upload de imagens                |
| python-dotenv                   | 1.0.1    | Variáveis de ambiente            |
| requests                        | 2.32.3   | Chamadas HTTP (geocoding, IA)    |
| beautifulsoup4                  | 4.12.3   | Scraping de URLs                 |
| anthropic                       | 0.49.0   | Claude API                       |
| psycopg2-binary                 | 2.9.10   | PostgreSQL (produção)            |
| whitenoise                      | 6.9.0    | Arquivos estáticos em produção   |

## Dependências de desenvolvimento

| Pacote        | Uso                              |
|---------------|----------------------------------|
| pytest        | Framework de testes              |
| pytest-django | Integração Django + pytest       |
| pytest-cov    | Cobertura de código              |
| factory-boy   | Factories para testes            |
| faker         | Dados falsos para testes         |
| black         | Formatação de código             |
| flake8        | Linting                          |
| isort         | Ordenação de imports             |

---


## ⚠️ Chaves de API

Todas as chaves de API do projeto estão armazenadas no **Bitwarden**.

- Item: `Plan N'Go — API Keys` (Secure Note)
- Acesse em: [bitwarden.com](https://bitwarden.com) ou pela extensão do browser

| Variável | Serviço | Onde obter |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| `ANTHROPIC_API_KEY` | Anthropic Claude | [console.anthropic.com](https://console.anthropic.com) |
| `UNSPLASH_ACCESS_KEY` | Unsplash | [unsplash.com/developers](https://unsplash.com/developers) |
| `GOOGLE_PLACES_API_KEY` | Google Places | [console.cloud.google.com](https://console.cloud.google.com) |

> Para configurar um novo ambiente: copie o `.env.example` para `.env`
> e preencha com as chaves do Bitwarden.

```bash
cp .env.example .env
# edite o .env com as chaves do Bitwarden
```


## Banco de dados

### Desenvolvimento (SQLite)

Usado automaticamente quando `DATABASE_URL` não está definido no `.env`.

```bash
python manage.py migrate
```

### Produção (PostgreSQL)

Configure no `.env`:

```
DATABASE_URL=postgresql://usuario:senha@localhost:5432/plango
```

---

## Servidor de desenvolvimento

```bash
cd ~/workspace/plan-n-go
python manage.py runserver
```

Acesse: `http://localhost:8000`

Admin: `http://localhost:8000/admin`

---

## Criar superusuário

```bash
python manage.py createsuperuser
```

---

## Ativar o ambiente virtual

O pyenv ativa automaticamente ao entrar na pasta do projeto. Se necessário:

```bash
pyenv activate plan-n-go-venv
```
