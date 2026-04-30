"""
Plan N'Go — Configurações do Django
Python 3.13 + Django 6.0
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# =============================================================================
# Caminhos base
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis do arquivo .env
load_dotenv(BASE_DIR / ".env")
# IA Backend
AI_BACKEND       = os.environ.get("AI_BACKEND", "gemini")
GEMINI_API_KEY            = os.environ.get("GEMINI_API_KEY", "")
GOOGLE_CUSTOM_SEARCH_KEY  = os.environ.get("GOOGLE_CUSTOM_SEARCH_KEY", "")
UNSPLASH_ACCESS_KEY       = os.environ.get("UNSPLASH_ACCESS_KEY", "")
GOOGLE_CUSTOM_SEARCH_CX   = os.environ.get("GOOGLE_CUSTOM_SEARCH_CX", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


# =============================================================================
# Segurança
# =============================================================================
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-troque-em-producao")

DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# =============================================================================
# Apps instalados
# =============================================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Terceiros
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",

    # Apps do Plan'Go
    "accounts",
    "destinations",
    "lists",
    "roteiros",
    "feed",
]

# =============================================================================
# Middlewares
# =============================================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # arquivos estáticos em produção
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# =============================================================================
# URLs
# =============================================================================
ROOT_URLCONF = "plango.urls"

# =============================================================================
# Templates
# =============================================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # ↓ Django vai procurar templates nesta pasta
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# =============================================================================
# WSGI
# =============================================================================
WSGI_APPLICATION = "plango.wsgi.application"

# =============================================================================
# Banco de dados
# =============================================================================
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # PostgreSQL (produção)
    import urllib.parse
    parsed = urllib.parse.urlparse(DATABASE_URL)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME":     parsed.path.lstrip("/"),
            "USER":     parsed.username,
            "PASSWORD": parsed.password,
            "HOST":     parsed.hostname,
            "PORT":     parsed.port or 5432,
        }
    }
else:
    # SQLite (desenvolvimento)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME":   BASE_DIR / "db.sqlite3",
        }
    }

# =============================================================================
# Model de usuário customizado
# =============================================================================
AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# =============================================================================
# Validação de senha
# =============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =============================================================================
# Internacionalização
# =============================================================================
LANGUAGE_CODE = "pt-br"
TIME_ZONE     = "America/Sao_Paulo"
USE_I18N      = True
USE_TZ        = True

# =============================================================================
# Arquivos estáticos (CSS, JS, imagens)
# =============================================================================
STATIC_URL = "/static/"

# ↓ Django vai procurar arquivos estáticos nesta pasta durante o desenvolvimento
STATICFILES_DIRS = [BASE_DIR / "static"]

# ↓ Pasta onde o collectstatic coleta tudo para produção
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise — compressão e cache de arquivos estáticos em produção
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# =============================================================================
# Uploads de mídia (fotos de perfil, fotos de destinos)
# =============================================================================
MEDIA_URL  = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =============================================================================
# Django REST Framework
# =============================================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# =============================================================================
# JWT (SimpleJWT)
# =============================================================================
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS":  True,
}

# =============================================================================
# CORS (permite o frontend React se comunicar com o backend)
# =============================================================================
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

CORS_ALLOWED_ORIGINS = [FRONTEND_URL]

CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# E-mail
# =============================================================================
EMAIL_BACKEND    = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@plango.app")

# =============================================================================
# Anthropic (Claude API)
# =============================================================================
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# =============================================================================
# Autenticação — redirecionamentos
# =============================================================================
LOGIN_URL          = "/accounts/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

# =============================================================================
# Mensagens do Django (usa a sessão)
# =============================================================================
from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG:   "debug",
    messages.INFO:    "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR:   "error",
}

# =============================================================================
# Chave primária padrão
# =============================================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
