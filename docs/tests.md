# Testes

## Configuração

Arquivo: `pytest.ini`

```ini
[pytest]
DJANGO_SETTINGS_MODULE = plango.settings
python_files = tests/*.py tests/**/*.py
addopts = --cov=. --cov-report=term-missing --cov-report=html -v
```

---

## Rodar os testes

```bash
# Todos os testes
cd ~/workspace/plan-n-go
pytest

# App específico
pytest accounts/tests/ -v
pytest destinations/tests/ -v

# Salvar resultado em arquivo
pytest accounts/tests/ -v > ~/Downloads/test_results.txt 2>&1

# Ver enquanto roda e salvar
pytest accounts/tests/ -v | tee ~/Downloads/test_results.txt

# Relatório HTML de cobertura
pytest --cov-report=html
# Abrir htmlcov/index.html no navegador
```

---

## Testes por app

### accounts (28 testes)

Localização: `accounts/tests/test_accounts.py`

| Classe                  | Testes | Cobertura                                       |
|-------------------------|--------|-------------------------------------------------|
| `TestRegister`          | 8      | Cadastro, e-mail duplicado, senha curta, e-mail de confirmação |
| `TestConfirmEmail`      | 5      | Ativação, login automático, token inválido, confirmação dupla  |
| `TestProfileSetup`      | 7      | Salvar perfil, pular, nacionalidade, nome público |
| `TestLogin`             | 5      | Login, senha errada, case-insensitive, inativo  |
| `TestLogout`            | 3      | Logout, redirecionamento, GET retorna 405       |
| `TestEmailAuthBackend`  | 4      | Autenticação, case-insensitive, inativo         |

### destinations (12 testes)

Localização: `destinations/tests/test_geocoding.py`

| Classe                    | Testes | Cobertura                                    |
|---------------------------|--------|----------------------------------------------|
| `TestNominatimBackend`    | 6      | Sugestões, continente, query curta, erro de rede, deduplicação |
| `TestGeocodingFactory`    | 3      | Nominatim padrão, Google quando configurado  |
| `TestAutocompleteView`    | 5      | Login requerido, query curta, retorno JSON   |

---

## Cobertura atual

```
accounts/         ~92%
destinations/     ~73%
plango/           ~94%
Total             ~85%
```

---

## Fixtures principais

```python
@pytest.fixture
def active_user(db):
    return User.objects.create_user(
        email="viajante@plango.app",
        name="Viajante Teste",
        password="senha@1234",
        is_active=True,
        email_verified=True,
    )

@pytest.fixture
def inactive_user(db):
    # Usuário recém-cadastrado, aguardando confirmação de e-mail
    return User.objects.create_user(..., is_active=False)
```

---

## Convenção de commits para testes

```
test: adiciona testes para <funcionalidade>
fix:  corrige teste <nome> — FIX <descrição do problema>
```
