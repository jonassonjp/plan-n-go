"""
Plan N'Go — Testes do app accounts (fluxo com verificação de e-mail)
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail

User = get_user_model()

# =============================================================
# Fixtures
# =============================================================

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
    return User.objects.create_user(
        email="novo@plango.app",
        name="Novo Usuário",
        password="senha@1234",
        is_active=False,
        email_verified=False,
    )


# =============================================================
# Cadastro
# =============================================================

class TestRegister:

    def test_pagina_carrega(self, client):
        response = client.get(reverse("accounts:register"))
        assert response.status_code == 200

    def test_cadastro_cria_usuario_inativo(self, client, db):
        client.post(reverse("accounts:register"), {
            "name":     "João Silva",
            "email":    "joao@plango.app",
            "password": "senha@1234",
        })
        user = User.objects.get(email="joao@plango.app")
        assert user.is_active is False
        assert user.email_verified is False

    def test_cadastro_envia_email_confirmacao(self, client, db):
        client.post(reverse("accounts:register"), {
            "name":     "João Silva",
            "email":    "joao@plango.app",
            "password": "senha@1234",
        })
        assert len(mail.outbox) == 1
        assert "joao@plango.app" in mail.outbox[0].to
        assert "confirme" in mail.outbox[0].subject.lower()

    def test_cadastro_email_contem_link_confirmacao(self, client, db):
        client.post(reverse("accounts:register"), {
            "name":     "João Silva",
            "email":    "joao@plango.app",
            "password": "senha@1234",
        })
        user = User.objects.get(email="joao@plango.app")
        assert str(user.email_token) in mail.outbox[0].body

    def test_cadastro_redireciona_para_pagina_done(self, client, db):
        response = client.post(reverse("accounts:register"), {
            "name":     "João Silva",
            "email":    "joao@plango.app",
            "password": "senha@1234",
        })
        assert response.status_code == 200
        assert b"Verifique" in response.content

    def test_cadastro_email_duplicado(self, client, active_user):
        response = client.post(reverse("accounts:register"), {
            "name":     "Outro",
            "email":    "viajante@plango.app",
            "password": "senha@1234",
        })
        assert response.status_code == 200
        assert User.objects.filter(email="viajante@plango.app").count() == 1

    def test_cadastro_senha_curta(self, client, db):
        client.post(reverse("accounts:register"), {
            "name":     "Teste",
            "email":    "teste@plango.app",
            "password": "123",
        })
        assert not User.objects.filter(email="teste@plango.app").exists()

    def test_cadastro_campos_vazios(self, client, db):
        client.post(reverse("accounts:register"), {
            "name": "", "email": "", "password": "",
        })
        assert User.objects.count() == 0

    def test_usuario_nao_loga_antes_de_confirmar(self, client, db):
        client.post(reverse("accounts:register"), {
            "name":     "Pendente",
            "email":    "pendente@plango.app",
            "password": "senha@1234",
        })
        # Tenta login antes de confirmar
        client.post(reverse("accounts:login"), {
            "email":    "pendente@plango.app",
            "password": "senha@1234",
        })
        assert "_auth_user_id" not in client.session


# =============================================================
# Confirmação de e-mail
# =============================================================

class TestConfirmEmail:

    def test_confirmacao_ativa_usuario(self, client, inactive_user):
        url = reverse("accounts:confirm_email",
                      kwargs={"token": inactive_user.email_token})
        client.get(url)
        inactive_user.refresh_from_db()
        assert inactive_user.is_active is True
        assert inactive_user.email_verified is True

    def test_confirmacao_loga_usuario(self, client, inactive_user):
        url = reverse("accounts:confirm_email",
                      kwargs={"token": inactive_user.email_token})
        client.get(url)
        assert "_auth_user_id" in client.session

    def test_confirmacao_redireciona_para_perfil(self, client, inactive_user):
        url = reverse("accounts:confirm_email",
                      kwargs={"token": inactive_user.email_token})
        response = client.get(url)
        assert response["Location"] == reverse("accounts:profile_setup")

    def test_token_invalido_retorna_404(self, client, db):
        import uuid
        url = reverse("accounts:confirm_email",
                      kwargs={"token": uuid.uuid4()})
        response = client.get(url)
        assert response.status_code == 404

    def test_confirmacao_dupla_redireciona_para_login(self, client, inactive_user):
        url = reverse("accounts:confirm_email",
                      kwargs={"token": inactive_user.email_token})
        client.get(url)          # primeira confirmação
        client.logout()
        response = client.get(url)  # segunda tentativa
        assert response["Location"] == reverse("accounts:login")


# =============================================================
# Setup de Perfil
# =============================================================

class TestProfileSetup:

    def test_pagina_requer_login(self, client, db):
        response = client.get(reverse("accounts:profile_setup"))
        assert response.status_code == 302

    def test_pagina_carrega_para_usuario_logado(self, client, active_user):
        client.force_login(active_user)
        response = client.get(reverse("accounts:profile_setup"))
        assert response.status_code == 200

    def test_salva_nacionalidade(self, client, active_user):
        client.force_login(active_user)
        client.post(reverse("accounts:profile_setup"), {
            "nationality":   "BR",
            "display_name":  "",
        })
        active_user.refresh_from_db()
        assert active_user.nationality == "BR"

    def test_salva_nome_publico(self, client, active_user):
        client.force_login(active_user)
        client.post(reverse("accounts:profile_setup"), {
            "nationality":  "BR",
            "display_name": "Viajante JP",
        })
        active_user.refresh_from_db()
        assert active_user.display_name == "Viajante JP"

    def test_nome_publico_vazio_usa_nome_completo(self, client, active_user):
        client.force_login(active_user)
        client.post(reverse("accounts:profile_setup"), {
            "nationality":  "BR",
            "display_name": "",
        })
        active_user.refresh_from_db()
        assert active_user.public_name == active_user.name

    def test_salvo_redireciona_para_dashboard(self, client, active_user):
        client.force_login(active_user)
        response = client.post(reverse("accounts:profile_setup"), {
            "nationality":  "BR",
            "display_name": "JP",
        })
        assert response["Location"] == reverse("destinations:dashboard")

    def test_pular_redireciona_para_dashboard(self, client, active_user):
        client.force_login(active_user)
        response = client.post(reverse("accounts:profile_setup"), {"skip": "1"})
        assert response["Location"] == reverse("destinations:dashboard")


# =============================================================
# Login
# =============================================================

class TestLogin:

    def test_pagina_carrega(self, client):
        assert client.get(reverse("accounts:login")).status_code == 200

    def test_login_sucesso(self, client, active_user):
        response = client.post(reverse("accounts:login"), {
            "email":    "viajante@plango.app",
            "password": "senha@1234",
        })
        assert response.status_code == 302
        assert "_auth_user_id" in client.session

    def test_login_senha_errada(self, client, active_user):
        client.post(reverse("accounts:login"), {
            "email":    "viajante@plango.app",
            "password": "errada",
        })
        assert "_auth_user_id" not in client.session

    def test_login_email_case_insensitive(self, client, active_user):
        response = client.post(reverse("accounts:login"), {
            "email":    "VIAJANTE@PLANGO.APP",
            "password": "senha@1234",
        })
        assert response.status_code == 302

    def test_usuario_inativo_nao_loga(self, client, inactive_user):
        client.post(reverse("accounts:login"), {
            "email":    "novo@plango.app",
            "password": "senha@1234",
        })
        assert "_auth_user_id" not in client.session


# =============================================================
# Logout
# =============================================================

class TestLogout:

    def test_logout_sucesso(self, client, active_user):
        client.force_login(active_user)
        client.post(reverse("accounts:logout"))
        assert "_auth_user_id" not in client.session

    def test_logout_redireciona_para_home(self, client, active_user):
        client.force_login(active_user)
        response = client.post(reverse("accounts:logout"))
        assert response["Location"] == reverse("index")

    def test_logout_requer_post(self, client, active_user):
        client.force_login(active_user)
        assert client.get(reverse("accounts:logout")).status_code == 405


# =============================================================
# Backend de autenticação
# =============================================================

class TestEmailAuthBackend:

    def test_autentica_por_email(self, db, active_user):
        from accounts.backends import EmailAuthBackend
        result = EmailAuthBackend().authenticate(
            None, username="viajante@plango.app", password="senha@1234")
        assert result == active_user

    def test_falha_senha_errada(self, db, active_user):
        from accounts.backends import EmailAuthBackend
        assert EmailAuthBackend().authenticate(
            None, username="viajante@plango.app", password="errada") is None

    def test_email_case_insensitive(self, db, active_user):
        from accounts.backends import EmailAuthBackend
        result = EmailAuthBackend().authenticate(
            None, username="VIAJANTE@PLANGO.APP", password="senha@1234")
        assert result == active_user

    def test_inativo_nao_autentica(self, db, inactive_user):
        from accounts.backends import EmailAuthBackend
        assert EmailAuthBackend().authenticate(
            None, username="novo@plango.app", password="senha@1234") is None
