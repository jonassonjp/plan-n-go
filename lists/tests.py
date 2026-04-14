"""
Plan N'Go — Testes do app lists
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from lists.models import DestinationList, ListItem
from destinations.models import Destination

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
def dest_japan(db, user):
    return Destination.objects.create(
        user=user,
        name="Tóquio",
        country="Japão",
        continent="Ásia",
        languages=["Japonês"],
        best_months=[3, 4, 11],
    )


@pytest.fixture
def dest_france(db, user):
    return Destination.objects.create(
        user=user,
        name="Paris",
        country="França",
        continent="Europa",
        languages=["Francês"],
        best_months=[4, 5, 9],
    )


@pytest.fixture
def dest_brazil(db, user):
    return Destination.objects.create(
        user=user,
        name="Rio de Janeiro",
        country="Brasil",
        continent="América do Sul",
        languages=["Português"],
        best_months=[12, 1, 2],
    )


@pytest.fixture
def manual_list(db, user):
    return DestinationList.objects.create(
        user=user,
        name="Favoritos",
        emoji="❤️",
        list_type=DestinationList.TYPE_MANUAL,
    )


@pytest.fixture
def smart_list(db, user):
    return DestinationList.objects.create(
        user=user,
        name="Destinos Asiáticos",
        emoji="🌏",
        list_type=DestinationList.TYPE_SMART,
        smart_criteria={"continents": ["Ásia"]},
    )


# =============================================================
# Model: DestinationList
# =============================================================

class TestDestinationListModel:

    def test_cria_lista_manual(self, manual_list):
        assert manual_list.pk is not None
        assert manual_list.list_type == DestinationList.TYPE_MANUAL
        assert manual_list.is_smart is False

    def test_cria_lista_inteligente(self, smart_list):
        assert smart_list.is_smart is True
        assert smart_list.smart_criteria["continents"] == ["Ásia"]

    def test_slug_gerado_automaticamente(self, manual_list):
        assert manual_list.slug != ""
        assert "favoritos" in manual_list.slug

    def test_str(self, manual_list, user):
        assert "Favoritos" in str(manual_list)

    def test_lista_manual_get_destinations_vazia(self, manual_list):
        assert manual_list.destination_count() == 0

    def test_lista_manual_get_destinations_com_itens(
        self, manual_list, dest_japan, dest_france
    ):
        ListItem.objects.create(destination_list=manual_list, destination=dest_japan, position=0)
        ListItem.objects.create(destination_list=manual_list, destination=dest_france, position=1)
        assert manual_list.destination_count() == 2

    def test_lista_inteligente_filtra_por_continente(
        self, smart_list, dest_japan, dest_france, dest_brazil
    ):
        # smart_list filtra "Ásia" — só Tóquio deve aparecer
        destinations = list(smart_list.get_destinations())
        assert dest_japan in destinations
        assert dest_france not in destinations
        assert dest_brazil not in destinations

    def test_lista_inteligente_filtra_por_idioma(self, db, user, dest_japan, dest_france):
        lst = DestinationList.objects.create(
            user=user,
            name="Francófonos",
            list_type=DestinationList.TYPE_SMART,
            smart_criteria={"languages": ["Francês"]},
        )
        destinations = list(lst.get_destinations())
        assert dest_france in destinations
        assert dest_japan not in destinations

    def test_lista_inteligente_filtra_por_mes(self, db, user, dest_japan, dest_brazil):
        # Dezembro: dest_brazil tem [12,1,2], dest_japan tem [3,4,11]
        lst = DestinationList.objects.create(
            user=user,
            name="Verão",
            list_type=DestinationList.TYPE_SMART,
            smart_criteria={"months": [12]},
        )
        destinations = list(lst.get_destinations())
        assert dest_brazil in destinations
        assert dest_japan not in destinations

    def test_lista_inteligente_sem_criterios_retorna_tudo(
        self, db, user, dest_japan, dest_france, dest_brazil
    ):
        lst = DestinationList.objects.create(
            user=user,
            name="Todos",
            list_type=DestinationList.TYPE_SMART,
            smart_criteria={},
        )
        assert lst.destination_count() == 3

    def test_destino_pode_estar_em_varias_listas(
        self, db, user, dest_japan, manual_list
    ):
        lst2 = DestinationList.objects.create(
            user=user, name="Segunda Lista", list_type=DestinationList.TYPE_MANUAL
        )
        ListItem.objects.create(destination_list=manual_list, destination=dest_japan, position=0)
        ListItem.objects.create(destination_list=lst2, destination=dest_japan, position=0)
        assert manual_list.destination_count() == 1
        assert lst2.destination_count() == 1


# =============================================================
# Model: ListItem
# =============================================================

class TestListItemModel:

    def test_cria_item(self, manual_list, dest_japan):
        item = ListItem.objects.create(
            destination_list=manual_list, destination=dest_japan, position=0
        )
        assert item.pk is not None

    def test_item_unico_por_lista(self, manual_list, dest_japan):
        ListItem.objects.create(
            destination_list=manual_list, destination=dest_japan, position=0
        )
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            ListItem.objects.create(
                destination_list=manual_list, destination=dest_japan, position=1
            )

    def test_str(self, manual_list, dest_japan):
        item = ListItem.objects.create(
            destination_list=manual_list, destination=dest_japan, position=0
        )
        assert "Favoritos" in str(item)
        assert "Tóquio" in str(item)


# =============================================================
# Views: Dashboard
# =============================================================

class TestListsDashboard:

    def test_requer_login(self, client):
        response = client.get(reverse("lists:dashboard"))
        assert response.status_code == 302
        assert "/accounts/" in response["Location"]

    def test_dashboard_carrega(self, logged_client):
        response = logged_client.get(reverse("lists:dashboard"))
        assert response.status_code == 200

    def test_dashboard_exibe_listas_do_usuario(
        self, logged_client, manual_list, smart_list
    ):
        response = logged_client.get(reverse("lists:dashboard"))
        content = response.content.decode()
        assert "Favoritos" in content
        assert "Destinos Asiáticos" in content

    def test_dashboard_nao_exibe_listas_de_outro_usuario(
        self, logged_client, other_user, db
    ):
        DestinationList.objects.create(
            user=other_user, name="Lista Alheia", list_type=DestinationList.TYPE_MANUAL
        )
        response = logged_client.get(reverse("lists:dashboard"))
        assert "Lista Alheia" not in response.content.decode()


# =============================================================
# Views: Criar lista
# =============================================================

class TestListCreate:

    def test_requer_login(self, client):
        response = client.post(reverse("lists:create"), {"name": "Nova"})
        assert response.status_code == 302

    def test_cria_lista_manual(self, logged_client):
        response = logged_client.post(reverse("lists:create"), {
            "name": "Minha Lista",
            "emoji": "🌍",
            "list_type": "manual",
            "description": "Uma lista de teste",
        })
        assert response.status_code == 302
        assert DestinationList.objects.filter(name="Minha Lista").exists()

    def test_cria_lista_inteligente_com_criterios(self, logged_client):
        response = logged_client.post(reverse("lists:create"), {
            "name": "Destinos Europeus",
            "emoji": "🏰",
            "list_type": "smart",
            "criteria_continents": ["Europa"],
            "criteria_languages": ["Francês", "Italiano"],
        })
        assert response.status_code == 302
        lst = DestinationList.objects.get(name="Destinos Europeus")
        assert lst.list_type == DestinationList.TYPE_SMART
        assert "Europa" in lst.smart_criteria["continents"]
        assert "Francês" in lst.smart_criteria["languages"]

    def test_nome_obrigatorio(self, logged_client):
        logged_client.post(reverse("lists:create"), {"name": "", "list_type": "manual"})
        assert not DestinationList.objects.filter(name="").exists()

    def test_redireciona_para_detalhe_apos_criar(self, logged_client):
        response = logged_client.post(reverse("lists:create"), {
            "name": "Nova Lista",
            "list_type": "manual",
            "emoji": "📍",
        })
        lst = DestinationList.objects.get(name="Nova Lista")
        assert response["Location"].endswith(reverse("lists:detail", kwargs={"pk": lst.pk}))


# =============================================================
# Views: Detalhe
# =============================================================

class TestListDetail:

    def test_requer_login(self, client, manual_list):
        response = client.get(reverse("lists:detail", kwargs={"pk": manual_list.pk}))
        assert response.status_code == 302

    def test_detalhe_carrega(self, logged_client, manual_list):
        response = logged_client.get(reverse("lists:detail", kwargs={"pk": manual_list.pk}))
        assert response.status_code == 200

    def test_detalhe_exibe_destinos(self, logged_client, manual_list, dest_japan):
        ListItem.objects.create(
            destination_list=manual_list, destination=dest_japan, position=0
        )
        response = logged_client.get(reverse("lists:detail", kwargs={"pk": manual_list.pk}))
        assert "Tóquio" in response.content.decode()

    def test_outro_usuario_nao_acessa(self, client, other_user, manual_list):
        client.force_login(other_user)
        response = client.get(reverse("lists:detail", kwargs={"pk": manual_list.pk}))
        assert response.status_code == 404


# =============================================================
# Views: Editar lista
# =============================================================

class TestListEdit:

    def test_edita_lista(self, logged_client, manual_list):
        logged_client.post(
            reverse("lists:edit", kwargs={"pk": manual_list.pk}),
            {"name": "Favoritos Editado", "emoji": "⭐", "description": ""},
        )
        manual_list.refresh_from_db()
        assert manual_list.name == "Favoritos Editado"
        assert manual_list.emoji == "⭐"

    def test_outro_usuario_nao_edita(self, client, other_user, manual_list):
        client.force_login(other_user)
        response = client.post(
            reverse("lists:edit", kwargs={"pk": manual_list.pk}),
            {"name": "Hackeado", "emoji": "💀"},
        )
        assert response.status_code == 404
        manual_list.refresh_from_db()
        assert manual_list.name == "Favoritos"


# =============================================================
# Views: Excluir lista
# =============================================================

class TestListDelete:

    def test_exclui_lista(self, logged_client, manual_list):
        pk = manual_list.pk
        logged_client.post(reverse("lists:delete", kwargs={"pk": pk}))
        assert not DestinationList.objects.filter(pk=pk).exists()

    def test_outro_usuario_nao_exclui(self, client, other_user, manual_list):
        client.force_login(other_user)
        client.post(reverse("lists:delete", kwargs={"pk": manual_list.pk}))
        assert DestinationList.objects.filter(pk=manual_list.pk).exists()


# =============================================================
# Views: Adicionar / Remover destinos (lista manual)
# =============================================================

class TestListManageDestinations:

    def test_adiciona_destino(self, logged_client, manual_list, dest_japan):
        logged_client.post(
            reverse("lists:add_destination", kwargs={"pk": manual_list.pk}),
            {"destination_id": dest_japan.pk},
        )
        assert ListItem.objects.filter(
            destination_list=manual_list, destination=dest_japan
        ).exists()

    def test_adiciona_destino_de_outro_usuario_falha(
        self, logged_client, manual_list, other_user, db
    ):
        dest_other = Destination.objects.create(
            user=other_user, name="Destino Alheio", country="X",
        )
        response = logged_client.post(
            reverse("lists:add_destination", kwargs={"pk": manual_list.pk}),
            {"destination_id": dest_other.pk},
        )
        assert response.status_code == 404

    def test_remove_destino(self, logged_client, manual_list, dest_japan):
        ListItem.objects.create(
            destination_list=manual_list, destination=dest_japan, position=0
        )
        logged_client.post(
            reverse("lists:remove_destination",
                    kwargs={"pk": manual_list.pk, "dest_pk": dest_japan.pk}),
        )
        assert not ListItem.objects.filter(
            destination_list=manual_list, destination=dest_japan
        ).exists()

    def test_posicao_incrementa(self, logged_client, manual_list, dest_japan, dest_france):
        logged_client.post(
            reverse("lists:add_destination", kwargs={"pk": manual_list.pk}),
            {"destination_id": dest_japan.pk},
        )
        logged_client.post(
            reverse("lists:add_destination", kwargs={"pk": manual_list.pk}),
            {"destination_id": dest_france.pk},
        )
        items = ListItem.objects.filter(destination_list=manual_list).order_by("position")
        assert items[0].destination == dest_japan
        assert items[1].destination == dest_france
        assert items[1].position > items[0].position


# =============================================================
# Views: API JSON
# =============================================================

class TestApiListsForDestination:

    def test_retorna_json(self, logged_client, manual_list, dest_japan):
        response = logged_client.get(
            reverse("lists:api_lists_for_destination", kwargs={"dest_pk": dest_japan.pk})
        )
        assert response.status_code == 200
        data = response.json()
        assert "lists" in data
        assert any(l["id"] == manual_list.pk for l in data["lists"])

    def test_has_destination_false_quando_ausente(self, logged_client, manual_list, dest_japan):
        response = logged_client.get(
            reverse("lists:api_lists_for_destination", kwargs={"dest_pk": dest_japan.pk})
        )
        entry = next(l for l in response.json()["lists"] if l["id"] == manual_list.pk)
        assert entry["has_destination"] is False

    def test_has_destination_true_quando_presente(
        self, logged_client, manual_list, dest_japan
    ):
        ListItem.objects.create(
            destination_list=manual_list, destination=dest_japan, position=0
        )
        response = logged_client.get(
            reverse("lists:api_lists_for_destination", kwargs={"dest_pk": dest_japan.pk})
        )
        entry = next(l for l in response.json()["lists"] if l["id"] == manual_list.pk)
        assert entry["has_destination"] is True

    def test_nao_inclui_listas_inteligentes(self, logged_client, smart_list, dest_japan):
        response = logged_client.get(
            reverse("lists:api_lists_for_destination", kwargs={"dest_pk": dest_japan.pk})
        )
        ids = [l["id"] for l in response.json()["lists"]]
        assert smart_list.pk not in ids


class TestApiToggleDestination:

    def test_toggle_adiciona(self, logged_client, manual_list, dest_japan):
        import json
        response = logged_client.post(
            reverse("lists:api_toggle", kwargs={"pk": manual_list.pk}),
            data=json.dumps({"destination_id": dest_japan.pk}),
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["action"] == "added"
        assert ListItem.objects.filter(
            destination_list=manual_list, destination=dest_japan
        ).exists()

    def test_toggle_remove(self, logged_client, manual_list, dest_japan):
        import json
        ListItem.objects.create(
            destination_list=manual_list, destination=dest_japan, position=0
        )
        response = logged_client.post(
            reverse("lists:api_toggle", kwargs={"pk": manual_list.pk}),
            data=json.dumps({"destination_id": dest_japan.pk}),
            content_type="application/json",
        )
        assert response.json()["action"] == "removed"
        assert not ListItem.objects.filter(
            destination_list=manual_list, destination=dest_japan
        ).exists()
