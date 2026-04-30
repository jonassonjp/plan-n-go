"""
Plan N'Go — Testes do app feed (feed público / descobrir)
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from destinations.models import Destination
from roteiros.models import Roteiro, Dia, Indicacao

User = get_user_model()


# =============================================================
# Fixtures
# =============================================================

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="viajante@plango.app",
        name="Viajante Teste",
        password="senha@1234",
        is_active=True,
        email_verified=True,
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        email="outro@plango.app",
        name="Outro Usuário",
        password="senha@1234",
        is_active=True,
        email_verified=True,
    )


@pytest.fixture
def logged_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def destination(db, other_user):
    """Destino público e ativo pertencente a other_user."""
    return Destination.objects.create(
        user=other_user,
        name="Tóquio",
        country="Japão",
        continent="Ásia",
        currency="JPY",
        languages=["Japonês"],
        visibility=Destination.VISIBILITY_PUBLIC,
        status=Destination.STATUS_ACTIVE,
    )


@pytest.fixture
def private_destination(db, other_user):
    """Destino privado pertencente a other_user."""
    return Destination.objects.create(
        user=other_user,
        name="Seoul",
        country="Coreia do Sul",
        continent="Ásia",
        visibility=Destination.VISIBILITY_PRIVATE,
        status=Destination.STATUS_ACTIVE,
    )


@pytest.fixture
def other_user_destination(db, other_user):
    """Destino ativo (privado) de other_user usado como base para roteiros."""
    return Destination.objects.create(
        user=other_user,
        name="Paris",
        country="França",
        continent="Europa",
        currency="EUR",
        visibility=Destination.VISIBILITY_PRIVATE,
        status=Destination.STATUS_ACTIVE,
    )


@pytest.fixture
def public_roteiro(db, other_user, other_user_destination):
    """Roteiro público pertencente a other_user."""
    roteiro = Roteiro.objects.create(
        user=other_user,
        destination=other_user_destination,
        title="Paris em 3 dias",
        visibility=Roteiro.VISIBILITY_PUBLIC,
    )
    dia = Dia.objects.create(roteiro=roteiro, numero=1, titulo="Chegada")
    Indicacao.objects.create(
        dia=dia,
        tipo=Indicacao.TIPO_TURISMO,
        nome="Torre Eiffel",
        descricao="Visita ao ícone de Paris.",
        ordem=0,
    )
    return roteiro


@pytest.fixture
def private_roteiro(db, other_user, other_user_destination):
    """Roteiro privado pertencente a other_user."""
    return Roteiro.objects.create(
        user=other_user,
        destination=other_user_destination,
        title="Roteiro secreto",
        visibility=Roteiro.VISIBILITY_PRIVATE,
    )


# =============================================================
# TestFeedView
# =============================================================

class TestFeedView:

    def test_feed_accessible_without_login(self, client, destination):
        url = reverse("feed:feed")
        response = client.get(url)
        assert response.status_code == 200

    def test_feed_shows_public_destinations(self, client, destination):
        url = reverse("feed:feed")
        response = client.get(url)
        assert destination.name.encode() in response.content

    def test_feed_hides_private_destinations(self, client, private_destination):
        url = reverse("feed:feed")
        response = client.get(url)
        assert private_destination.name.encode() not in response.content

    def test_feed_default_tab_is_destinos(self, client, destination):
        url = reverse("feed:feed")
        response = client.get(url)
        assert b"feed-tab--active" in response.content
        # Verifica que o contexto tem tab == 'destinos'
        assert response.context["tab"] == "destinos"

    def test_feed_tab_roteiros_shows_roteiros(self, client, public_roteiro):
        url = reverse("feed:feed") + "?tab=roteiros"
        response = client.get(url)
        assert response.status_code == 200
        assert public_roteiro.title.encode() in response.content

    def test_feed_tab_roteiros_hides_private(self, client, private_roteiro):
        url = reverse("feed:feed") + "?tab=roteiros"
        response = client.get(url)
        assert private_roteiro.title.encode() not in response.content

    def test_feed_continent_filter(self, client, destination, private_destination):
        """Filtrar por continente 'Ásia' retorna destino público asiático."""
        url = reverse("feed:feed") + "?tab=destinos&continente=Ásia"
        response = client.get(url)
        assert response.status_code == 200
        assert destination.name.encode() in response.content
        assert response.context["continente_ativo"] == "Ásia"

    def test_feed_continent_filter_excludes_other_continent(
        self, client, db, other_user
    ):
        """Filtrar por 'Europa' não traz destinos asiáticos."""
        asian = Destination.objects.create(
            user=other_user,
            name="Bangkok",
            country="Tailândia",
            continent="Ásia",
            visibility=Destination.VISIBILITY_PUBLIC,
            status=Destination.STATUS_ACTIVE,
        )
        url = reverse("feed:feed") + "?tab=destinos&continente=Europa"
        response = client.get(url)
        assert asian.name.encode() not in response.content

    def test_feed_continentes_context(self, client, destination):
        """O contexto 'continentes' contém o continente do destino público."""
        url = reverse("feed:feed")
        response = client.get(url)
        assert "Ásia" in list(response.context["continentes"])


# =============================================================
# TestPublicDestinationDetail
# =============================================================

class TestPublicDestinationDetail:

    def test_200_for_public_destination(self, client, destination):
        url = reverse("feed:public_destination_detail", args=[destination.pk])
        response = client.get(url)
        assert response.status_code == 200
        assert destination.name.encode() in response.content

    def test_404_for_private_destination(self, client, private_destination):
        url = reverse("feed:public_destination_detail", args=[private_destination.pk])
        response = client.get(url)
        assert response.status_code == 404

    def test_404_for_nonexistent_destination(self, client, db):
        url = reverse("feed:public_destination_detail", args=[99999])
        response = client.get(url)
        assert response.status_code == 404

    def test_shows_author_name(self, client, destination, other_user):
        url = reverse("feed:public_destination_detail", args=[destination.pk])
        response = client.get(url)
        assert other_user.public_name.encode() in response.content

    def test_back_link_goes_to_feed(self, client, destination):
        url = reverse("feed:public_destination_detail", args=[destination.pk])
        response = client.get(url)
        feed_url = reverse("feed:feed")
        assert feed_url.encode() in response.content

    def test_accessible_without_login(self, client, destination):
        url = reverse("feed:public_destination_detail", args=[destination.pk])
        response = client.get(url)
        assert response.status_code == 200


# =============================================================
# TestPublicRoteiroDetail
# =============================================================

class TestPublicRoteiroDetail:

    def test_200_for_public_roteiro(self, client, public_roteiro):
        url = reverse("feed:public_roteiro_detail", args=[public_roteiro.pk])
        response = client.get(url)
        assert response.status_code == 200
        assert public_roteiro.title.encode() in response.content

    def test_404_for_private_roteiro(self, client, private_roteiro):
        url = reverse("feed:public_roteiro_detail", args=[private_roteiro.pk])
        response = client.get(url)
        assert response.status_code == 404

    def test_404_for_nonexistent_roteiro(self, client, db):
        url = reverse("feed:public_roteiro_detail", args=[99999])
        response = client.get(url)
        assert response.status_code == 404

    def test_shows_dias_and_indicacoes(self, client, public_roteiro):
        url = reverse("feed:public_roteiro_detail", args=[public_roteiro.pk])
        response = client.get(url)
        # Dia criado no fixture
        assert b"Torre Eiffel" in response.content

    def test_logged_in_user_sees_copy_form(self, logged_client, user, public_roteiro):
        # Cria um destino ativo para o user logado
        dest = Destination.objects.create(
            user=user,
            name="Meu Destino",
            country="Brasil",
            status=Destination.STATUS_ACTIVE,
        )
        url = reverse("feed:public_roteiro_detail", args=[public_roteiro.pk])
        response = logged_client.get(url)
        assert response.status_code == 200
        copy_url = reverse("roteiros:copy", args=[public_roteiro.pk])
        assert copy_url.encode() in response.content
        assert b"Meu Destino" in response.content

    def test_anonymous_user_sees_login_prompt(self, client, public_roteiro):
        url = reverse("feed:public_roteiro_detail", args=[public_roteiro.pk])
        response = client.get(url)
        login_url = reverse("accounts:login")
        assert login_url.encode() in response.content

    def test_logged_in_no_destinations_shows_add_link(
        self, logged_client, public_roteiro
    ):
        """Usuário logado sem destinos vê link para adicionar destino."""
        url = reverse("feed:public_roteiro_detail", args=[public_roteiro.pk])
        response = logged_client.get(url)
        destinations_url = reverse("destinations:dashboard")
        assert destinations_url.encode() in response.content

    def test_shows_author_name(self, client, public_roteiro, other_user):
        url = reverse("feed:public_roteiro_detail", args=[public_roteiro.pk])
        response = client.get(url)
        assert other_user.public_name.encode() in response.content
