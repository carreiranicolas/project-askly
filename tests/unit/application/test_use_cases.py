"""Tests for application use cases."""

from unittest.mock import MagicMock, Mock

import pytest

from src.application.dtos import AlterarStatusDTO, ChamadoCreateDTO, LoginDTO
from src.application.use_cases import ChangeStatusUseCase, CreateTicketUseCase, LoginUseCase
from src.domain.enums import Prioridade, StatusChamado
from src.domain.exceptions import InvalidCredentialsException, UserInactiveException
from tests.fixtures.factories import CategoriaFactory, ChamadoFactory, UsuarioFactory


class TestLoginUseCase:
    """Tests for LoginUseCase."""

    def test_login_success(self):
        """Test successful login."""
        usuario = UsuarioFactory()

        repo = Mock()
        repo.get_by_email.return_value = usuario

        hasher = Mock()
        hasher.verify.return_value = True

        use_case = LoginUseCase(usuario_repository=repo, password_hasher=hasher)

        dto = LoginDTO(email=usuario.email, senha="password")
        result = use_case.execute(dto)

        assert result.usuario.id == usuario.id
        assert result.usuario.email == usuario.email

    def test_login_invalid_email(self):
        """Test login with invalid email."""
        repo = Mock()
        repo.get_by_email.return_value = None

        hasher = Mock()

        use_case = LoginUseCase(usuario_repository=repo, password_hasher=hasher)

        dto = LoginDTO(email="invalid@test.com", senha="password")

        with pytest.raises(InvalidCredentialsException):
            use_case.execute(dto)

    def test_login_invalid_password(self):
        """Test login with invalid password."""
        usuario = UsuarioFactory()

        repo = Mock()
        repo.get_by_email.return_value = usuario

        hasher = Mock()
        hasher.verify.return_value = False

        use_case = LoginUseCase(usuario_repository=repo, password_hasher=hasher)

        dto = LoginDTO(email=usuario.email, senha="wrong")

        with pytest.raises(InvalidCredentialsException):
            use_case.execute(dto)

    def test_login_inactive_user(self):
        """Test login with inactive user."""
        usuario = UsuarioFactory(inativo=True)

        repo = Mock()
        repo.get_by_email.return_value = usuario

        hasher = Mock()
        hasher.verify.return_value = True

        use_case = LoginUseCase(usuario_repository=repo, password_hasher=hasher)

        dto = LoginDTO(email=usuario.email, senha="password")

        with pytest.raises(UserInactiveException):
            use_case.execute(dto)


class TestCreateTicketUseCase:
    """Tests for CreateTicketUseCase."""

    def test_create_ticket_success(self):
        """Test successful ticket creation."""
        solicitante = UsuarioFactory()
        categoria = CategoriaFactory()

        uow = MagicMock()
        uow.categorias.get_by_id.return_value = categoria
        uow.chamados.add.return_value = None
        uow.historico_status.add.return_value = None
        uow.__enter__ = Mock(return_value=uow)
        uow.__exit__ = Mock(return_value=False)

        use_case = CreateTicketUseCase(unit_of_work=uow)

        dto = ChamadoCreateDTO(
            titulo="Test Ticket",
            descricao="Test description",
            categoria_id=categoria.id,
            prioridade=Prioridade.MEDIA,
        )

        result = use_case.execute(dto, solicitante)

        assert result.titulo == "Test Ticket"
        assert result.status_atual == "ABERTO"

        uow.chamados.add.assert_called_once()
        uow.historico_status.add.assert_called_once()
        uow.commit.assert_called_once()


class TestChangeStatusUseCase:
    """Tests for ChangeStatusUseCase."""

    def test_change_status_success(self):
        """Test successful status change."""
        atendente = UsuarioFactory(atendente=True)
        chamado = ChamadoFactory(status_atual=StatusChamado.ABERTO)
        categoria = CategoriaFactory()
        solicitante = UsuarioFactory()

        uow = MagicMock()
        uow.chamados.get_by_id.return_value = chamado
        uow.chamados.update.return_value = chamado
        uow.historico_status.add.return_value = None
        uow.categorias.get_by_id.return_value = categoria
        uow.usuarios.get_by_id.return_value = solicitante
        uow.__enter__ = Mock(return_value=uow)
        uow.__exit__ = Mock(return_value=False)

        chamado.solicitante_id = solicitante.id
        chamado.categoria_id = categoria.id

        use_case = ChangeStatusUseCase(unit_of_work=uow)

        dto = AlterarStatusDTO(
            chamado_id=chamado.id,
            novo_status=StatusChamado.EM_ATENDIMENTO,
            motivo="Iniciando atendimento",
        )

        result = use_case.execute(dto, atendente)

        assert result.status_atual == "EM_ATENDIMENTO"

        uow.chamados.update.assert_called_once()
        uow.historico_status.add.assert_called_once()
        uow.commit.assert_called_once()
