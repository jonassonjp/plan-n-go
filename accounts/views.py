"""
Plan N'Go — Views do app accounts
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_POST


NATIONALITIES = [
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

    return render(request, "accounts/auth.html", {
        "mode":         "login",
        "nationalities": NATIONALITIES,
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect("destinations:dashboard")

    if request.method == "POST":
        from .models import User

        name        = request.POST.get("name", "").strip()
        email       = request.POST.get("email", "").strip()
        password    = request.POST.get("password", "")
        nationality = request.POST.get("nationality", "")
        avatar      = request.FILES.get("avatar")

        # Validações básicas
        if not name or not email or not password:
            messages.error(request, "Preencha todos os campos obrigatórios.")
            return render(request, "accounts/auth.html", {
                "mode":         "register",
                "nationalities": NATIONALITIES,
            })

        if len(password) < 8:
            messages.error(request, "A senha deve ter pelo menos 8 caracteres.")
            return render(request, "accounts/auth.html", {
                "mode":         "register",
                "nationalities": NATIONALITIES,
            })

        if User.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está cadastrado.")
            return render(request, "accounts/auth.html", {
                "mode":         "register",
                "nationalities": NATIONALITIES,
            })

        # Criar usuário — is_active=True por enquanto (e-mail verify depois)
        user = User.objects.create_user(
            email=email,
            name=name,
            password=password,
            nationality=nationality,
        )
        if avatar:
            user.avatar = avatar
            user.save()

        # Ativar direto (verificação por e-mail será implementada depois)
        user.is_active = True
        user.save()

        messages.success(request, f"Bem-vindo, {user.first_name}! Sua conta foi criada.")
        login(request, user)
        return redirect("destinations:dashboard")

    return render(request, "accounts/auth.html", {
        "mode":         "register",
        "nationalities": NATIONALITIES,
    })


@require_POST
def logout_view(request):
    logout(request)
    return redirect("index")
