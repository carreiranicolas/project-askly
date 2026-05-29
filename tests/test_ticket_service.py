"""Testes da lógica de domínio de chamados (`app/services/ticket_service.py`).

Aqui o foco é a lógica "pura" do serviço, complementando os testes de fluxo
HTTP em `test_tickets.py`:
  - `parse_status`: aceitar nome do enum ("EM_ATENDIMENTO") ou rótulo
    ("Em Atendimento") e rejeitar inválidos;
  - `allowed_transitions`: a máquina de estados (terminais, reabertura etc.);
  - SLA: cálculo de prazo, atraso e rótulo legível, manipulando `created_at`;
  - `dashboard_metrics`: a contagem agregada por status/área.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.extensions import db
from app.models.ticket import StatusEnum
from app.services import auth_service, ticket_service
from app.services.exceptions import ValidationError


def _novo_chamado(categoria_id, prioridade_id, email="dono@test.com"):
    """Cria um usuário Solicitante e um chamado dele; devolve (user, ticket).

    Usado pelos testes que precisam de um chamado real no banco para exercitar
    SLA e métricas. Roda assumindo um app_context já ativo.
    """
    user = auth_service.register("Dono", email, "Senha123")
    ticket = ticket_service.create_ticket(
        user,
        title="Chamado de teste",
        description="descricao",
        category_id=categoria_id,
        priority_id=prioridade_id,
    )
    return user, ticket


# ----------------------------- parse_status -----------------------------
def test_parse_status_aceita_nome_do_enum(app):
    with app.app_context():
        assert ticket_service.parse_status("EM_ATENDIMENTO") is StatusEnum.EM_ATENDIMENTO


def test_parse_status_aceita_rotulo(app):
    """O rótulo legível ("Em Atendimento") também deve ser aceito."""
    with app.app_context():
        assert ticket_service.parse_status("Em Atendimento") is StatusEnum.EM_ATENDIMENTO


def test_parse_status_invalido_gera_validacao(app):
    with app.app_context():
        with pytest.raises(ValidationError):
            ticket_service.parse_status("STATUS_QUE_NAO_EXISTE")


# -------------------------- allowed_transitions --------------------------
def test_cancelado_e_terminal(app):
    """De CANCELADO não há saída (estado terminal)."""
    with app.app_context():
        assert ticket_service.allowed_transitions(StatusEnum.CANCELADO) == []


def test_fechado_so_permite_reabrir(app):
    """De FECHADO a única transição é voltar para ABERTO (reabertura)."""
    with app.app_context():
        assert ticket_service.allowed_transitions(StatusEnum.FECHADO) == [StatusEnum.ABERTO]


def test_aguardando_aprovacao_fecha_ou_reabre(app):
    """De AGUARDANDO_APROVACAO: aprovar (-> Fechado) ou reabrir (-> Aberto)."""
    with app.app_context():
        opcoes = ticket_service.allowed_transitions(StatusEnum.AGUARDANDO_APROVACAO)
        assert set(opcoes) == {StatusEnum.FECHADO, StatusEnum.ABERTO}


def test_estado_ativo_pode_cancelar_e_enviar_para_aprovacao(app):
    """De um estado ativo (ABERTO) sempre dá para cancelar ou pedir aprovação."""
    with app.app_context():
        opcoes = ticket_service.allowed_transitions(StatusEnum.ABERTO)
        assert StatusEnum.CANCELADO in opcoes
        assert StatusEnum.AGUARDANDO_APROVACAO in opcoes
        assert StatusEnum.ABERTO not in opcoes  # não "transiciona" para si mesmo


# --------------------------------- SLA ---------------------------------
def test_sla_deadline_soma_horas_da_prioridade(app, catalog):
    """O prazo do SLA é created_at + sla_hours da prioridade (Alta = 8h)."""
    with app.app_context():
        _, ticket = _novo_chamado(catalog["categoria"], catalog["prioridade"])
        esperado = ticket.created_at + timedelta(hours=8)
        assert ticket_service.sla_deadline(ticket) == esperado


def test_is_overdue_true_quando_prazo_estourou(app, catalog):
    """Recuando o created_at para 10h atrás (SLA 8h), o chamado fica atrasado."""
    with app.app_context():
        _, ticket = _novo_chamado(catalog["categoria"], catalog["prioridade"])
        ticket.created_at = datetime.now(timezone.utc) - timedelta(hours=10)
        db.session.commit()
        assert ticket_service.is_overdue(ticket) is True
        # E o rótulo deve indicar atraso.
        assert "Atrasado" in ticket_service.sla_remaining_label(ticket)


def test_is_overdue_false_em_estado_que_para_o_sla(app, catalog):
    """Mesmo vencido, um chamado FECHADO não conta como atrasado (SLA parado)."""
    with app.app_context():
        _, ticket = _novo_chamado(catalog["categoria"], catalog["prioridade"])
        ticket.created_at = datetime.now(timezone.utc) - timedelta(hours=10)
        ticket.status = StatusEnum.FECHADO
        db.session.commit()
        assert ticket_service.is_overdue(ticket) is False
        assert ticket_service.sla_remaining_label(ticket) == "SLA pausado"


# ----------------------------- Dashboard -----------------------------
def test_dashboard_metrics_conta_abertos(app, catalog):
    """Um chamado recém-criado (ABERTO) deve contar como 1 total e 1 em aberto."""
    with app.app_context():
        user, _ = _novo_chamado(catalog["categoria"], catalog["prioridade"])
        metrics = ticket_service.dashboard_metrics(user)
        assert metrics["total"] == 1
        assert metrics["abertos"] == 1
        assert metrics["fechados"] == 0
