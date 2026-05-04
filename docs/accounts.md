# Autenticação e Cadastro

## Fluxo completo

```
1. /accounts/register/     → usuário preenche nome, e-mail e senha
2. E-mail de confirmação   → enviado automaticamente
3. /accounts/confirm/<token>/ → ativa a conta e loga automaticamente
4. /accounts/profile/setup/   → completa o perfil (foto, nome público, nacionalidade)
5. /destinations/          → dashboard principal
```

---

## URLs

| URL                              | View               | Descrição                        |
|----------------------------------|--------------------|----------------------------------|
| `GET/POST /accounts/register/`   | `register_view`    | Formulário de cadastro           |
| `GET /accounts/confirm/<token>/` | `confirm_email_view` | Ativa a conta via token UUID   |
| `GET/POST /accounts/profile/setup/` | `profile_setup_view` | Completa o perfil            |
| `GET/POST /accounts/login/`      | `login_view`       | Login por e-mail                 |
| `POST /accounts/logout/`         | `logout_view`      | Logout (requer POST)             |
| `GET/POST /accounts/password-reset/` | `PasswordResetView` | Formulário de redefinição de senha |
| `GET /accounts/password-reset/done/` | `PasswordResetDoneView` | Confirmação de envio do link |
| `GET/POST /accounts/reset/<uidb64>/<token>/` | `PasswordResetConfirmView` | Nova senha |
| `GET /accounts/reset/done/` | `PasswordResetCompleteView` | Senha redefinida com sucesso |

---

## Model User

Localização: `accounts/models.py`

Herda de `AbstractBaseUser` + `PermissionsMixin`.  
Login feito por **e-mail** (não username).

### Campos

| Campo            | Tipo          | Descrição                                           |
|------------------|---------------|-----------------------------------------------------|
| `email`          | EmailField    | Único, usado como USERNAME_FIELD                    |
| `name`           | CharField     | Nome completo                                       |
| `display_name`   | CharField     | Nome público (apelido). Se vazio, usa `name`        |
| `nationality`    | CharField     | Código ISO do país (ex: BR, US)                     |
| `avatar`         | ImageField    | Foto de perfil (upload para `avatars/`)             |
| `is_active`      | BooleanField  | `False` até confirmar e-mail                        |
| `email_verified` | BooleanField  | `True` após clicar no link de confirmação           |
| `email_token`    | UUIDField     | Token único para confirmação de e-mail              |

### Properties

```python
user.first_name   # → primeiro nome (ex: "Jonas")
user.public_name  # → display_name se preenchido, senão name
user.initials     # → iniciais dos dois primeiros nomes (ex: "JP")
```

---

## Backend de autenticação por e-mail

Localização: `accounts/backends.py`

```python
AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailAuthBackend",
    "django.contrib.auth.backends.ModelBackend",  # fallback para admin
]
```

Características:
- Busca usuário por `email__iexact` (case-insensitive)
- Usuários inativos não autenticam
- Compatível com múltiplos backends (passa `backend=` no `login()`)

---

## E-mail de confirmação

Em desenvolvimento, o e-mail é **impresso no terminal** (não enviado):

```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

O link de confirmação aparece no output do `runserver`. Exemplo:

```
Subject: Confirme seu e-mail — Plan N'Go
...
http://localhost:8000/accounts/confirm/550e8400-e29b-41d4-a716-446655440000/
```

---

## Redefinição de senha

Fluxo padrão do Django (`django.contrib.auth.views`):

1. Usuário acessa `/accounts/password-reset/` e informa o e-mail
2. E-mail com link único é enviado (em dev: impresso no terminal)
3. Usuário clica no link `/accounts/reset/<uidb64>/<token>/` e define nova senha
4. Redirecionado para `/accounts/reset/done/` com mensagem de sucesso

O link para redefinição também está disponível na página de perfil (`/accounts/profile/setup/`).

---

## Comandos de gerenciamento (dev)

| Comando | Descrição |
|---|---|
| `python manage.py set_passwords_to_123` | Redefine a senha de todos os usuários para `123` |
| `python manage.py set_superuser <email>` | Promove um usuário a superusuário por e-mail |

---

## Validações de cadastro

- Nome: obrigatório
- E-mail: obrigatório, único, formato válido
- Senha: mínimo 8 caracteres
- E-mail duplicado: retorna erro amigável
