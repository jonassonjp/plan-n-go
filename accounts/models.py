from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid


class UserManager(BaseUserManager):

    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        email = self.normalize_email(email)
        user  = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff",     True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active",    True)
        extra_fields.setdefault("email_verified", True)
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    NATIONALITY_CHOICES = [
        ("BR",    "🇧🇷 Brasil"),
        ("PT",    "🇵🇹 Portugal"),
        ("US",    "🇺🇸 Estados Unidos"),
        ("AR",    "🇦🇷 Argentina"),
        ("ES",    "🇪🇸 Espanha"),
        ("FR",    "🇫🇷 França"),
        ("DE",    "🇩🇪 Alemanha"),
        ("IT",    "🇮🇹 Itália"),
        ("JP",    "🇯🇵 Japão"),
        ("CN",    "🇨🇳 China"),
        ("MX",    "🇲🇽 México"),
        ("CO",    "🇨🇴 Colômbia"),
        ("CL",    "🇨🇱 Chile"),
        ("OTHER", "Outro"),
    ]

    # --- Campos de cadastro (passo 1) ---
    email    = models.EmailField(unique=True, verbose_name="E-mail")
    name     = models.CharField(max_length=150, verbose_name="Nome completo")
    password = models.CharField(max_length=128)

    # --- Campos de perfil (passo 2 — após confirmar e-mail) ---
    display_name = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Nome público",
        help_text="Como você quer ser chamado pelos outros usuários. "
                  "Se não preencher, usaremos seu nome completo.",
    )
    nationality = models.CharField(
        max_length=10,
        choices=NATIONALITY_CHOICES,
        blank=True,
        verbose_name="Nacionalidade",
        help_text="Usada para sugerir automaticamente informações de visto "
                  "para cada destino que você catalogar.",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Foto de perfil",
        help_text="Aparece no seu perfil público e nos roteiros compartilhados.",
    )

    # --- Verificação de e-mail ---
    is_active       = models.BooleanField(default=False)   # ativo só após confirmar e-mail
    email_verified  = models.BooleanField(default=False)
    email_token     = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # --- Controle ---
    is_staff    = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name        = "Usuário"
        verbose_name_plural = "Usuários"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"

    @property
    def first_name(self):
        return self.name.split()[0] if self.name else ""

    @property
    def public_name(self):
        """Nome que aparece para outros usuários."""
        return self.display_name.strip() or self.name

    @property
    def initials(self):
        """Iniciais dos dois primeiros nomes. Ex: Jonas Pereira → JP"""
        parts = self.name.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        elif len(parts) == 1:
            return parts[0][:2].upper()
        return "?"
