from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    NATIONALITY_CHOICES = [
        ("BR", "🇧🇷 Brasil"),
        ("PT", "🇵🇹 Portugal"),
        ("US", "🇺🇸 Estados Unidos"),
        ("AR", "🇦🇷 Argentina"),
        ("ES", "🇪🇸 Espanha"),
        ("FR", "🇫🇷 França"),
        ("DE", "🇩🇪 Alemanha"),
        ("IT", "🇮🇹 Itália"),
        ("JP", "🇯🇵 Japão"),
        ("CN", "🇨🇳 China"),
        ("MX", "🇲🇽 México"),
        ("CO", "🇨🇴 Colômbia"),
        ("CL", "🇨🇱 Chile"),
        ("OTHER", "Outro"),
    ]

    email       = models.EmailField(unique=True, verbose_name="E-mail")
    name        = models.CharField(max_length=150, verbose_name="Nome completo")
    nationality = models.CharField(
        max_length=10,
        choices=NATIONALITY_CHOICES,
        blank=True,
        verbose_name="Nacionalidade",
    )
    avatar      = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Foto de perfil",
    )
    is_active        = models.BooleanField(default=False)  # False até confirmar e-mail
    is_staff         = models.BooleanField(default=False)
    email_verified   = models.BooleanField(default=False)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

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
