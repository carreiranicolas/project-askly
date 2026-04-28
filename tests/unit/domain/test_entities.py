"""Tests for domain entities."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from src.domain.entities import Chamado, HistoricoStatus, Usuario
from src.domain.enums import PerfilUsuario, Prioridade, StatusChamado
from src.domain.exceptions import (
    AuthorizationException,
    InvalidStatusTransitionException,
    ReopenDeadlineExpiredException,
    TicketClosedException,
)
from tests.fixtures.factories import ChamadoFactory, UsuarioFactory


class TestUsuario:
    """Tests for Usuario entity."""

    def test_create_usuario(self):
        """Test user creation."""
        usuario = UsuarioFactory()

        assert usuario.id is not None
        assert usuario.nome
        assert usuario.email
        assert usuario.perfil == PerfilUsuario.SOLICITANTE
        assert usuario.ativo is True

    def test_usuario_is_admin(self):
        """Test admin check."""
        admin = UsuarioFactory(admin=True)
        solicitante = UsuarioFactory()

        assert admin.is_admin is True
        assert solicitante.is_admin is False

    def test_usuario_pode_ver_todos_chamados(self):
        """Test permission to see all tickets."""
        admin = UsuarioFactory(admin=True)
        atendente = UsuarioFactory(atendente=True)
        solicitante = UsuarioFactory()

        assert admin.pode_ver_todos_chamados() is True
        assert atendente.pode_ver_todos_chamados() is True
        assert solicitante.pode_ver_todos_chamados() is False

    def test_usuario_email_normalization(self):
        """Test email is normalized to lowercase."""
        usuario = Usuario(
            nome="Test",
            email="TEST@EMAIL.COM",
            perfil=PerfilUsuario.SOLICITANTE,
        )

        assert usuario.email == "test@email.com"


class TestChamado:
    """Tests for Chamado entity."""

    def test_create_chamado(self):
        """Test ticket creation."""
        chamado = ChamadoFactory()

        assert chamado.id is not None
        assert chamado.titulo
        assert chamado.status_atual == StatusChamado.ABERTO
        assert chamado.prioridade == Prioridade.MEDIA

    def test_chamado_is_fechado(self):
        """Test closed status check."""
        aberto = ChamadoFactory()
        fechado = ChamadoFactory(fechado=True)

        assert aberto.is_fechado is False
        assert fechado.is_fechado is True

    def test_chamado_pode_reabrir_dentro_prazo(self):
        """Test reopening within deadline."""
        chamado = ChamadoFactory(
            status_atual=StatusChamado.RESOLVIDO,
            resolvido_em=datetime.now(timezone.utc) - timedelta(days=1),
        )

        assert chamado.pode_reabrir() is True

    def test_chamado_nao_pode_reabrir_fora_prazo(self):
        """Test reopening after deadline."""
        chamado = ChamadoFactory(
            status_atual=StatusChamado.RESOLVIDO,
            resolvido_em=datetime.now(timezone.utc) - timedelta(days=5),
        )

        assert chamado.pode_reabrir() is False

    def test_validar_transicao_valida(self):
        """Test valid status transition."""
        chamado = ChamadoFactory(status_atual=StatusChamado.ABERTO)
        atendente = UsuarioFactory(atendente=True)

        chamado.validar_transicao(StatusChamado.EM_ATENDIMENTO, atendente.perfil, atendente.id)

    def test_validar_transicao_invalida(self):
        """Test invalid status transition."""
        chamado = ChamadoFactory(status_atual=StatusChamado.ABERTO)
        atendente = UsuarioFactory(atendente=True)

        with pytest.raises(InvalidStatusTransitionException):
            chamado.validar_transicao(StatusChamado.FECHADO, atendente.perfil, atendente.id)

    def test_validar_transicao_sem_permissao(self):
        """Test transition without permission."""
        chamado = ChamadoFactory(status_atual=StatusChamado.ABERTO)
        solicitante = UsuarioFactory()

        with pytest.raises(AuthorizationException):
            chamado.validar_transicao(
                StatusChamado.EM_ATENDIMENTO, solicitante.perfil, solicitante.id
            )

    def test_validar_transicao_chamado_fechado(self):
        """Test transition on closed ticket."""
        chamado = ChamadoFactory(fechado=True)
        admin = UsuarioFactory(admin=True)

        with pytest.raises(TicketClosedException):
            chamado.validar_transicao(StatusChamado.ABERTO, admin.perfil, admin.id)

    def test_alterar_status(self):
        """Test status change."""
        chamado = ChamadoFactory(status_atual=StatusChamado.ABERTO)
        atendente = UsuarioFactory(atendente=True)

        chamado.alterar_status(StatusChamado.EM_ATENDIMENTO, atendente.perfil, atendente.id)

        assert chamado.status_atual == StatusChamado.EM_ATENDIMENTO

    def test_alterar_status_para_resolvido_define_data(self):
        """Test resolved status sets date."""
        chamado = ChamadoFactory(status_atual=StatusChamado.EM_ATENDIMENTO)
        atendente = UsuarioFactory(atendente=True)

        chamado.alterar_status(StatusChamado.RESOLVIDO, atendente.perfil, atendente.id)

        assert chamado.status_atual == StatusChamado.RESOLVIDO
        assert chamado.resolvido_em is not None


class TestHistoricoStatus:
    """Tests for HistoricoStatus entity."""

    def test_criar_para_novo_chamado(self):
        """Test creating history for new ticket."""
        chamado_id = uuid4()
        usuario_id = uuid4()

        historico = HistoricoStatus.criar_para_novo_chamado(chamado_id, usuario_id)

        assert historico.chamado_id == chamado_id
        assert historico.alterado_por_usuario_id == usuario_id
        assert historico.status_anterior == ""
        assert historico.status_novo == StatusChamado.ABERTO.value
        assert historico.is_criacao is True

    def test_criar_para_transicao(self):
        """Test creating history for transition."""
        chamado_id = uuid4()
        usuario_id = uuid4()

        historico = HistoricoStatus.criar_para_transicao(
            chamado_id=chamado_id,
            usuario_id=usuario_id,
            status_anterior=StatusChamado.ABERTO,
            status_novo=StatusChamado.EM_ATENDIMENTO,
            motivo="Iniciando atendimento",
        )

        assert historico.status_anterior == StatusChamado.ABERTO.value
        assert historico.status_novo == StatusChamado.EM_ATENDIMENTO.value
        assert historico.motivo == "Iniciando atendimento"
        assert historico.is_criacao is False
