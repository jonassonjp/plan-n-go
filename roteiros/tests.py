"""
Plan N'Go — Testes do app roteiros
"""

from decimal import Decimal

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
def destination(db, user):
    return Destination.objects.create(
        user=user,
        name="Tóquio",
        country="Japão",
        continent="Ásia",
        currency="JPY",
        languages=["Japonês"],
    )


@pytest.fixture
def db_destination_other(db, other_user):
    return Destination.objects.create(
        user=other_user,
        name="Paris",
        country="França",
        currency="EUR",
    )


@pytest.fixture
def roteiro(db, user, destination):
    return Roteiro.objects.create(
        user=user,
        destination=destination,
        title="Roteiro Japão",
        description="Uma semana em Tóquio",
        visibility=Roteiro.VISIBILITY_PRIVATE,
        custo_hospedagem=Decimal("50000"),
        custo_alimentacao=Decimal("20000"),
        taxa_cambio=Decimal("0.034"),
    )


@pytest.fixture
def public_roteiro(db, other_user, db_destination_other):
    return Roteiro.objects.create(
        user=other_user,
        destination=db_destination_other,
        title="Roteiro Público",
        visibility=Roteiro.VISIBILITY_PUBLIC,
    )


@pytest.fixture
def dia(db, roteiro):
    return Dia.objects.create(roteiro=roteiro, numero=1, titulo="Chegada")


@pytest.fixture
def indicacao(db, dia):
    return Indicacao.objects.create(
        dia=dia,
        tipo=Indicacao.TIPO_TURISMO,
        nome="Senso-ji",
        descricao="Templo budista histórico",
        ordem=0,
    )


# =============================================================
# Model: Roteiro
# =============================================================

class TestRoteiroModel:

    def test_cria_roteiro(self, roteiro):
        assert roteiro.pk is not None
        assert roteiro.title == "Roteiro Japão"

    def test_str(self, roteiro):
        assert "Roteiro Japão" in str(roteiro)
        assert "Tóquio" in str(roteiro)

    def test_moeda(self, roteiro):
        assert roteiro.moeda == "JPY"

    def test_num_dias_inicial(self, roteiro):
        assert roteiro.num_dias == 0

    def test_num_dias_com_dias(self, roteiro, dia):
        assert roteiro.num_dias == 1

    def test_custo_hospedagem_brl(self, roteiro):
        # 50000 * 0.034 = 1700.00
        assert roteiro.custo_hospedagem_brl == Decimal("1700.00")

    def test_custo_alimentacao_brl(self, roteiro):
        # 20000 * 0.034 = 680.00
        assert roteiro.custo_alimentacao_brl == Decimal("680.00")

    def test_custo_total_local(self, roteiro):
        assert roteiro.custo_total_local == Decimal("70000")

    def test_custo_total_brl(self, roteiro):
        # 70000 * 0.034 = 2380.00
        assert roteiro.custo_total_brl == Decimal("2380.00")

    def test_custo_none_sem_taxa_cambio(self, db, user, destination):
        r = Roteiro.objects.create(
            user=user,
            destination=destination,
            title="Sem câmbio",
            custo_hospedagem=Decimal("1000"),
        )
        assert r.custo_hospedagem_brl is None
        assert r.custo_total_brl is None

    def test_custo_total_local_none_sem_custos(self, db, user, destination):
        r = Roteiro.objects.create(
            user=user,
            destination=destination,
            title="Sem custos",
        )
        assert r.custo_total_local is None

    def test_visibilidade_padrao_privado(self, db, user, destination):
        r = Roteiro.objects.create(user=user, destination=destination, title="Privado")
        assert r.visibility == Roteiro.VISIBILITY_PRIVATE

    def test_ordenacao_por_updated_at(self, db, user, destination):
        Roteiro.objects.create(user=user, destination=destination, title="Primeiro")
        r2 = Roteiro.objects.create(user=user, destination=destination, title="Segundo")
        roteiros = list(Roteiro.objects.filter(user=user))
        assert roteiros[0] == r2  # mais recente primeiro


# =============================================================
# Model: Dia
# =============================================================

class TestDiaModel:

    def test_cria_dia(self, dia):
        assert dia.pk is not None
        assert dia.numero == 1

    def test_str_com_titulo(self, dia):
        assert "Dia 1" in str(dia)
        assert "Chegada" in str(dia)

    def test_str_sem_titulo(self, db, roteiro):
        dia = Dia.objects.create(roteiro=roteiro, numero=2)
        assert str(dia) == "Dia 2"

    def test_unique_together_roteiro_numero(self, db, roteiro, dia):
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            Dia.objects.create(roteiro=roteiro, numero=1)

    def test_ordenacao_por_numero(self, db, roteiro):
        Dia.objects.create(roteiro=roteiro, numero=3)
        Dia.objects.create(roteiro=roteiro, numero=1)
        Dia.objects.create(roteiro=roteiro, numero=2)
        numeros = list(roteiro.dias.values_list("numero", flat=True))
        assert numeros == [1, 2, 3]


# =============================================================
# Model: Indicacao
# =============================================================

class TestIndicacaoModel:

    def test_cria_indicacao(self, indicacao):
        assert indicacao.pk is not None
        assert indicacao.nome == "Senso-ji"

    def test_str(self, indicacao):
        assert "Ponto Turístico" in str(indicacao)
        assert "Senso-ji" in str(indicacao)

    def test_is_alimentacao_false_para_turismo(self, indicacao):
        assert indicacao.is_alimentacao is False

    def test_is_alimentacao_true_para_restaurante(self, db, dia):
        ind = Indicacao.objects.create(
            dia=dia, tipo=Indicacao.TIPO_RESTAURANTE, nome="Sushi", ordem=1
        )
        assert ind.is_alimentacao is True

    def test_is_alimentacao_true_para_cafe(self, db, dia):
        ind = Indicacao.objects.create(
            dia=dia, tipo=Indicacao.TIPO_CAFE, nome="Café", ordem=1
        )
        assert ind.is_alimentacao is True

    def test_is_alimentacao_true_para_mercado(self, db, dia):
        ind = Indicacao.objects.create(
            dia=dia, tipo=Indicacao.TIPO_MERCADO, nome="Mercado", ordem=1
        )
        assert ind.is_alimentacao is True

    def test_ordenacao_por_ordem(self, db, dia, indicacao):
        Indicacao.objects.create(dia=dia, tipo=Indicacao.TIPO_OUTRO, nome="C", ordem=2)
        Indicacao.objects.create(dia=dia, tipo=Indicacao.TIPO_OUTRO, nome="A", ordem=1)
        nomes = list(dia.indicacoes.values_list("nome", flat=True))
        assert nomes[0] == "Senso-ji"  # ordem=0 (fixture)
        assert nomes[1] == "A"         # ordem=1
        assert nomes[2] == "C"         # ordem=2


# =============================================================
# Views: Dashboard
# =============================================================

class TestRoteiroDashboard:

    def test_requer_login(self, client):
        response = client.get(reverse("roteiros:dashboard"))
        assert response.status_code == 302
        assert "/accounts/" in response["Location"]

    def test_dashboard_carrega(self, logged_client):
        response = logged_client.get(reverse("roteiros:dashboard"))
        assert response.status_code == 200

    def test_exibe_roteiros_do_usuario(self, logged_client, roteiro):
        response = logged_client.get(reverse("roteiros:dashboard"))
        assert "Roteiro Japão" in response.content.decode()

    def test_nao_exibe_roteiros_de_outro_usuario(self, logged_client, public_roteiro):
        response = logged_client.get(reverse("roteiros:dashboard"))
        assert "Roteiro Público" not in response.content.decode()


# =============================================================
# Views: Criar roteiro
# =============================================================

class TestRoteiroCreate:

    def test_requer_login(self, client, destination):
        response = client.post(
            reverse("roteiros:create", kwargs={"dest_pk": destination.pk}),
            {"title": "Novo"},
        )
        assert response.status_code == 302
        assert "/accounts/" in response["Location"]

    def test_get_exibe_formulario(self, logged_client, destination):
        response = logged_client.get(
            reverse("roteiros:create", kwargs={"dest_pk": destination.pk})
        )
        assert response.status_code == 200

    def test_cria_roteiro(self, logged_client, destination):
        logged_client.post(
            reverse("roteiros:create", kwargs={"dest_pk": destination.pk}),
            {
                "title": "Novo Roteiro",
                "description": "Descrição",
                "visibility": Roteiro.VISIBILITY_PRIVATE,
            },
        )
        assert Roteiro.objects.filter(title="Novo Roteiro").exists()

    def test_redireciona_para_detalhe(self, logged_client, destination):
        response = logged_client.post(
            reverse("roteiros:create", kwargs={"dest_pk": destination.pk}),
            {"title": "Meu Roteiro", "visibility": Roteiro.VISIBILITY_PRIVATE},
        )
        r = Roteiro.objects.get(title="Meu Roteiro")
        assert response.status_code == 302
        assert str(r.pk) in response["Location"]

    def test_titulo_obrigatorio(self, logged_client, destination):
        logged_client.post(
            reverse("roteiros:create", kwargs={"dest_pk": destination.pk}),
            {"title": "", "visibility": Roteiro.VISIBILITY_PRIVATE},
        )
        assert not Roteiro.objects.filter(destination=destination).exists()

    def test_destino_de_outro_usuario_retorna_404(self, logged_client, db_destination_other):
        response = logged_client.post(
            reverse("roteiros:create", kwargs={"dest_pk": db_destination_other.pk}),
            {"title": "Inválido"},
        )
        assert response.status_code == 404

    def test_salva_custos(self, logged_client, destination):
        logged_client.post(
            reverse("roteiros:create", kwargs={"dest_pk": destination.pk}),
            {
                "title": "Com Custos",
                "visibility": Roteiro.VISIBILITY_PRIVATE,
                "custo_hospedagem": "50000",
                "custo_alimentacao": "20000",
                "taxa_cambio": "0.034",
            },
        )
        r = Roteiro.objects.get(title="Com Custos")
        assert r.custo_hospedagem == Decimal("50000")
        assert r.taxa_cambio == Decimal("0.034")


# =============================================================
# Views: Detalhe
# =============================================================

class TestRoteiroDetail:

    def test_requer_login(self, client, roteiro):
        response = client.get(reverse("roteiros:detail", kwargs={"pk": roteiro.pk}))
        assert response.status_code == 302

    def test_detalhe_carrega(self, logged_client, roteiro):
        response = logged_client.get(reverse("roteiros:detail", kwargs={"pk": roteiro.pk}))
        assert response.status_code == 200
        assert "Roteiro Japão" in response.content.decode()

    def test_outro_usuario_nao_acessa(self, client, other_user, roteiro):
        client.force_login(other_user)
        response = client.get(reverse("roteiros:detail", kwargs={"pk": roteiro.pk}))
        assert response.status_code == 404

    def test_exibe_dias_e_indicacoes(self, logged_client, roteiro, dia, indicacao):
        response = logged_client.get(reverse("roteiros:detail", kwargs={"pk": roteiro.pk}))
        content = response.content.decode()
        assert "Chegada" in content
        assert "Senso-ji" in content


# =============================================================
# Views: Editar roteiro
# =============================================================

class TestRoteiroEdit:

    def test_edita_roteiro(self, logged_client, roteiro):
        logged_client.post(
            reverse("roteiros:edit", kwargs={"pk": roteiro.pk}),
            {
                "title": "Roteiro Atualizado",
                "description": "Nova descrição",
                "visibility": Roteiro.VISIBILITY_PUBLIC,
            },
        )
        roteiro.refresh_from_db()
        assert roteiro.title == "Roteiro Atualizado"
        assert roteiro.visibility == Roteiro.VISIBILITY_PUBLIC

    def test_titulo_obrigatorio_na_edicao(self, logged_client, roteiro):
        logged_client.post(
            reverse("roteiros:edit", kwargs={"pk": roteiro.pk}),
            {"title": "", "visibility": Roteiro.VISIBILITY_PRIVATE},
        )
        roteiro.refresh_from_db()
        assert roteiro.title == "Roteiro Japão"

    def test_outro_usuario_nao_edita(self, client, other_user, roteiro):
        client.force_login(other_user)
        response = client.post(
            reverse("roteiros:edit", kwargs={"pk": roteiro.pk}),
            {"title": "Hackeado", "visibility": Roteiro.VISIBILITY_PRIVATE},
        )
        assert response.status_code == 404
        roteiro.refresh_from_db()
        assert roteiro.title == "Roteiro Japão"


# =============================================================
# Views: Excluir roteiro
# =============================================================

class TestRoteiroDelete:

    def test_exclui_roteiro(self, logged_client, roteiro):
        pk = roteiro.pk
        logged_client.post(reverse("roteiros:delete", kwargs={"pk": pk}))
        assert not Roteiro.objects.filter(pk=pk).exists()

    def test_redireciona_para_dashboard(self, logged_client, roteiro):
        response = logged_client.post(reverse("roteiros:delete", kwargs={"pk": roteiro.pk}))
        assert response.status_code == 302
        assert response["Location"].endswith(reverse("roteiros:dashboard"))

    def test_outro_usuario_nao_exclui(self, client, other_user, roteiro):
        client.force_login(other_user)
        client.post(reverse("roteiros:delete", kwargs={"pk": roteiro.pk}))
        assert Roteiro.objects.filter(pk=roteiro.pk).exists()


# =============================================================
# Views: Copiar roteiro público
# =============================================================

class TestRoteiroCopy:

    def test_copia_roteiro_publico(self, logged_client, user, destination, public_roteiro):
        dest_user = Destination.objects.create(
            user=user, name="Paris (meu)", country="França"
        )
        response = logged_client.post(
            reverse("roteiros:copy", kwargs={"pk": public_roteiro.pk}),
            {"destination_id": dest_user.pk},
        )
        assert response.status_code == 302
        copia = Roteiro.objects.filter(user=user, copiado_de=public_roteiro).first()
        assert copia is not None
        assert copia.title == "Roteiro Público (cópia)"
        assert copia.visibility == Roteiro.VISIBILITY_PRIVATE

    def test_copia_inclui_dias_e_indicacoes(
        self, logged_client, user, other_user, db_destination_other
    ):
        roteiro_pub = Roteiro.objects.create(
            user=other_user,
            destination=db_destination_other,
            title="Roteiro Completo",
            visibility=Roteiro.VISIBILITY_PUBLIC,
        )
        dia_pub = Dia.objects.create(roteiro=roteiro_pub, numero=1, titulo="Dia Um")
        Indicacao.objects.create(
            dia=dia_pub, tipo=Indicacao.TIPO_TURISMO, nome="Torre Eiffel", ordem=0
        )

        dest_user = Destination.objects.create(
            user=user, name="Paris (meu)", country="França"
        )
        logged_client.post(
            reverse("roteiros:copy", kwargs={"pk": roteiro_pub.pk}),
            {"destination_id": dest_user.pk},
        )

        copia = Roteiro.objects.get(user=user, copiado_de=roteiro_pub)
        assert copia.dias.count() == 1
        dia_copia = copia.dias.first()
        assert dia_copia.titulo == "Dia Um"
        assert dia_copia.indicacoes.filter(nome="Torre Eiffel").exists()

    def test_nao_copia_roteiro_privado(self, logged_client, user, roteiro, destination):
        dest_user = Destination.objects.create(
            user=user, name="Outro", country="Japão"
        )
        response = logged_client.post(
            reverse("roteiros:copy", kwargs={"pk": roteiro.pk}),
            {"destination_id": dest_user.pk},
        )
        assert response.status_code == 404


# =============================================================
# Views: Dias
# =============================================================

class TestDiaAdd:

    def test_adiciona_dia(self, logged_client, roteiro):
        logged_client.post(
            reverse("roteiros:dia_add", kwargs={"pk": roteiro.pk}),
            {"titulo": "Primeiro Dia"},
        )
        assert roteiro.dias.filter(numero=1, titulo="Primeiro Dia").exists()

    def test_numero_incrementa(self, logged_client, roteiro, dia):
        logged_client.post(
            reverse("roteiros:dia_add", kwargs={"pk": roteiro.pk}),
            {"titulo": "Segundo Dia"},
        )
        assert roteiro.dias.filter(numero=2).exists()

    def test_outro_usuario_nao_adiciona(self, client, other_user, roteiro):
        client.force_login(other_user)
        response = client.post(
            reverse("roteiros:dia_add", kwargs={"pk": roteiro.pk}),
            {"titulo": "Dia Alheio"},
        )
        assert response.status_code == 404


class TestDiaEdit:

    def test_edita_dia(self, logged_client, roteiro, dia):
        logged_client.post(
            reverse("roteiros:dia_edit", kwargs={"pk": roteiro.pk, "dia_pk": dia.pk}),
            {"titulo": "Novo Título", "data": "2025-06-15"},
        )
        dia.refresh_from_db()
        assert dia.titulo == "Novo Título"
        assert str(dia.data) == "2025-06-15"

    def test_outro_usuario_nao_edita_dia(self, client, other_user, roteiro, dia):
        client.force_login(other_user)
        response = client.post(
            reverse("roteiros:dia_edit", kwargs={"pk": roteiro.pk, "dia_pk": dia.pk}),
            {"titulo": "Hackeado"},
        )
        assert response.status_code == 404


class TestDiaDelete:

    def test_exclui_dia(self, logged_client, roteiro, dia):
        pk = dia.pk
        logged_client.post(
            reverse("roteiros:dia_delete", kwargs={"pk": roteiro.pk, "dia_pk": dia.pk})
        )
        assert not Dia.objects.filter(pk=pk).exists()

    def test_renumera_dias_apos_exclusao(self, logged_client, roteiro):
        d1 = Dia.objects.create(roteiro=roteiro, numero=1)
        d2 = Dia.objects.create(roteiro=roteiro, numero=2)
        d3 = Dia.objects.create(roteiro=roteiro, numero=3)

        logged_client.post(
            reverse("roteiros:dia_delete", kwargs={"pk": roteiro.pk, "dia_pk": d2.pk})
        )

        d3.refresh_from_db()
        assert d3.numero == 2
        assert not Dia.objects.filter(pk=d2.pk).exists()

    def test_outro_usuario_nao_exclui_dia(self, client, other_user, roteiro, dia):
        client.force_login(other_user)
        response = client.post(
            reverse("roteiros:dia_delete", kwargs={"pk": roteiro.pk, "dia_pk": dia.pk})
        )
        assert response.status_code == 404
        assert Dia.objects.filter(pk=dia.pk).exists()


# =============================================================
# Views: Indicações
# =============================================================

class TestIndicacaoAdd:

    def test_adiciona_indicacao(self, logged_client, roteiro, dia):
        logged_client.post(
            reverse("roteiros:indicacao_add", kwargs={"pk": roteiro.pk, "dia_pk": dia.pk}),
            {
                "tipo": Indicacao.TIPO_RESTAURANTE,
                "nome": "Ichiran Ramen",
                "descricao": "Ramen famoso",
                "horario_sugerido": "12:00",
                "custo_estimado": "1500",
            },
        )
        assert dia.indicacoes.filter(nome="Ichiran Ramen").exists()

    def test_nome_obrigatorio(self, logged_client, roteiro, dia):
        logged_client.post(
            reverse("roteiros:indicacao_add", kwargs={"pk": roteiro.pk, "dia_pk": dia.pk}),
            {"tipo": Indicacao.TIPO_TURISMO, "nome": ""},
        )
        assert dia.indicacoes.count() == 0

    def test_ordem_incrementa(self, logged_client, roteiro, dia, indicacao):
        logged_client.post(
            reverse("roteiros:indicacao_add", kwargs={"pk": roteiro.pk, "dia_pk": dia.pk}),
            {"tipo": Indicacao.TIPO_TURISMO, "nome": "Segunda Indicação"},
        )
        segunda = dia.indicacoes.get(nome="Segunda Indicação")
        assert segunda.ordem > 0

    def test_outro_usuario_nao_adiciona(self, client, other_user, roteiro, dia):
        client.force_login(other_user)
        response = client.post(
            reverse("roteiros:indicacao_add", kwargs={"pk": roteiro.pk, "dia_pk": dia.pk}),
            {"tipo": Indicacao.TIPO_TURISMO, "nome": "Inválido"},
        )
        assert response.status_code == 404


class TestIndicacaoEdit:

    def test_edita_indicacao(self, logged_client, roteiro, indicacao):
        logged_client.post(
            reverse("roteiros:indicacao_edit",
                    kwargs={"pk": roteiro.pk, "ind_pk": indicacao.pk}),
            {
                "tipo": Indicacao.TIPO_ATIVIDADE,
                "nome": "Senso-ji Editado",
                "descricao": "Nova descrição",
                "custo_estimado": "500",
            },
        )
        indicacao.refresh_from_db()
        assert indicacao.nome == "Senso-ji Editado"
        assert indicacao.tipo == Indicacao.TIPO_ATIVIDADE
        assert indicacao.custo_estimado == Decimal("500")

    def test_nome_obrigatorio_na_edicao(self, logged_client, roteiro, indicacao):
        logged_client.post(
            reverse("roteiros:indicacao_edit",
                    kwargs={"pk": roteiro.pk, "ind_pk": indicacao.pk}),
            {"tipo": Indicacao.TIPO_TURISMO, "nome": ""},
        )
        indicacao.refresh_from_db()
        assert indicacao.nome == "Senso-ji"

    def test_outro_usuario_nao_edita(self, client, other_user, roteiro, indicacao):
        client.force_login(other_user)
        response = client.post(
            reverse("roteiros:indicacao_edit",
                    kwargs={"pk": roteiro.pk, "ind_pk": indicacao.pk}),
            {"tipo": Indicacao.TIPO_TURISMO, "nome": "Hackeado"},
        )
        assert response.status_code == 404
        indicacao.refresh_from_db()
        assert indicacao.nome == "Senso-ji"


class TestIndicacaoDelete:

    def test_exclui_indicacao(self, logged_client, roteiro, indicacao):
        pk = indicacao.pk
        logged_client.post(
            reverse("roteiros:indicacao_delete",
                    kwargs={"pk": roteiro.pk, "ind_pk": indicacao.pk})
        )
        assert not Indicacao.objects.filter(pk=pk).exists()

    def test_outro_usuario_nao_exclui(self, client, other_user, roteiro, indicacao):
        client.force_login(other_user)
        response = client.post(
            reverse("roteiros:indicacao_delete",
                    kwargs={"pk": roteiro.pk, "ind_pk": indicacao.pk})
        )
        assert response.status_code == 404
        assert Indicacao.objects.filter(pk=indicacao.pk).exists()


# =============================================================
# Views: Gerar IA
# =============================================================

class TestGenerateAI:

    def test_sem_api_key_retorna_erro(self, logged_client, roteiro, settings):
        settings.ANTHROPIC_API_KEY = ""
        response = logged_client.post(
            reverse("roteiros:generate_ai", kwargs={"pk": roteiro.pk}),
            {"num_dias": "3"},
        )
        assert response.status_code == 500
        assert "error" in response.json()

    def test_outro_usuario_nao_gera(self, client, other_user, roteiro):
        client.force_login(other_user)
        response = client.post(
            reverse("roteiros:generate_ai", kwargs={"pk": roteiro.pk}),
            {"num_dias": "3"},
        )
        assert response.status_code == 404
