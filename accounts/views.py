"""
Plan N'Go — Views do app accounts
Fluxo: cadastro → e-mail de confirmação → perfil → dashboard
"""

import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

EMAIL_BACKEND = "accounts.backends.EmailAuthBackend"

NATIONALITIES = [
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


# =============================================================
# Cadastro — apenas nome, e-mail e senha
# =============================================================
def register_view(request):
    if request.user.is_authenticated:
        return redirect("destinations:dashboard")

    if request.method == "POST":
        from .models import User

        name     = request.POST.get("name", "").strip()
        email    = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not name or not email or not password:
            messages.error(request, "Preencha todos os campos obrigatórios.")
            return render(request, "accounts/register.html")

        if len(password) < 8:
            messages.error(request, "A senha deve ter pelo menos 8 caracteres.")
            return render(request, "accounts/register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está cadastrado.")
            return render(request, "accounts/register.html")

        user = User.objects.create_user(
            email=email,
            name=name,
            password=password,
            is_active=False,   # inativo até confirmar e-mail
        )

        _send_confirmation_email(request, user)

        return render(request, "accounts/register_done.html", {"email": email})

    return render(request, "accounts/register.html")


def _send_confirmation_email(request, user):
    """Envia e-mail de confirmação com o link de ativação."""
    confirm_url = request.build_absolute_uri(
        f"/accounts/confirm/{user.email_token}/"
    )
    subject = "Confirme seu e-mail — Plan N'Go"
    body = (
        f"Olá, {user.first_name}!\n\n"
        f"Clique no link abaixo para confirmar seu e-mail e acessar o Plan N'Go:\n\n"
        f"{confirm_url}\n\n"
        f"Se você não criou uma conta, ignore este e-mail.\n\n"
        f"Equipe Plan N'Go"
    )
    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


# =============================================================
# Confirmação de e-mail
# =============================================================
def confirm_email_view(request, token):
    from .models import User

    user = get_object_or_404(User, email_token=token)

    if user.email_verified:
        # Já confirmado anteriormente — vai para login
        messages.info(request, "E-mail já confirmado. Faça login para continuar.")
        return redirect("accounts:login")

    # Ativar conta
    user.is_active      = True
    user.email_verified = True
    user.save()

    # Logar automaticamente e ir para o perfil
    login(request, user, backend=EMAIL_BACKEND)
    messages.success(request, f"E-mail confirmado! Complete seu perfil, {user.first_name}.")
    return redirect("accounts:profile_setup")


# =============================================================
# Configuração de perfil (pós-confirmação)
# =============================================================
@login_required
def profile_setup_view(request):
    user = request.user

    if request.method == "POST":
        name         = request.POST.get("name", "").strip()
        display_name = request.POST.get("display_name", "").strip()
        nationality  = request.POST.get("nationality", "").strip()
        new_email    = request.POST.get("email", "").strip().lower()
        avatar       = request.FILES.get("avatar")

        if name:
            user.name = name
        user.display_name = display_name
        user.nationality  = nationality
        if avatar:
            user.avatar = avatar

        email_change_pending = False
        if new_email and new_email != user.email:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                messages.error(request, "Este e-mail já está em uso por outra conta.")
                return redirect("accounts:profile_setup")
            user.pending_email = new_email
            user.email_change_token = uuid.uuid4()
            email_change_pending = True

        user.save()

        if email_change_pending:
            _send_email_change_confirmation(request, user)
            messages.info(
                request,
                f"Enviamos um link de confirmação para {user.pending_email}. "
                "Clique nele para concluir a troca de e-mail."
            )
        else:
            messages.success(request, "Perfil salvo com sucesso.")

        return redirect("accounts:profile_setup")

    return render(request, "accounts/profile_setup.html", {
        "nationalities": NATIONALITIES,
        "user":          user,
    })


# =============================================================
# Troca de e-mail — confirmação
# =============================================================
def _send_email_change_confirmation(request, user):
    confirm_url = request.build_absolute_uri(
        f"/accounts/email-change/confirm/{user.email_change_token}/"
    )
    subject = "Confirme seu novo e-mail — Plan N'Go"
    body = (
        f"Olá, {user.first_name}!\n\n"
        f"Recebemos uma solicitação para alterar o e-mail da sua conta para:\n"
        f"  {user.pending_email}\n\n"
        f"Clique no link abaixo para confirmar a troca:\n\n"
        f"{confirm_url}\n\n"
        f"Se você não solicitou essa alteração, ignore este e-mail — "
        f"seu e-mail atual permanece inalterado.\n\n"
        f"Equipe Plan N'Go"
    )
    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.pending_email],
        fail_silently=False,
    )


@login_required
def confirm_email_change_view(request, token):
    user = request.user
    if str(user.email_change_token) != str(token) or not user.pending_email:
        messages.error(request, "Link de confirmação inválido ou expirado.")
        return redirect("accounts:profile_setup")

    user.email = user.pending_email
    user.pending_email = ""
    user.email_change_token = None
    user.save()

    messages.success(request, f"E-mail atualizado para {user.email} com sucesso.")
    return redirect("accounts:profile_setup")


# =============================================================
# Login
# =============================================================
def login_view(request):
    if request.user.is_authenticated:
        return redirect("destinations:dashboard")

    if request.method == "POST":
        email    = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        user     = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("destinations:dashboard")
        else:
            messages.error(request, "E-mail ou senha incorretos.")

    return render(request, "accounts/login.html")


# =============================================================
# Logout
# =============================================================
@require_POST
def logout_view(request):
    logout(request)
    return redirect("index")
