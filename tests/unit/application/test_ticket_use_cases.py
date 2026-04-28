"""Tests for ticket use cases: Get, List, Assign, AddComment."""

from unittest.mock import MagicMock, Mock
from uuid import uuid4

import pytest

from src.application.dtos import AtribuirAtendenteDTO, ChamadoListFilterDTO, ComentarioCreateDTO
from src.application.use_cases import (
    AddCommentUseCase,
    AssignAttendantUseCase,
    GetTicketUseCase,
    ListTicketsUseCase,
)
from src.domain.enums import PerfilUsuario, StatusChamado
from src.domain.exceptions import (
    AuthorizationException,
    EntityNotFoundException,
    TicketClosedException,
    ValidationException,
)
from tests.fixtures.factories import (
    CategoriaFactory,
    ChamadoFactory,
    ComentarioFactory,
    UsuarioFactory,
)


def _make_uow():
    """Create a MagicMock UoW with context manager support."""
    uow = MagicMock()
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=False)
    return uow


class TestGetTicketUseCase:
    """Tests for GetTicketUseCase."""

    def test_get_ticket_success(self):
        """Test retrieving ticket details."""
        solicitante = UsuarioFactory()
        chamado = ChamadoFactory(solicitante_id=solicitante.id)
        categoria = CategoriaFactory()
        chamado.categoria_id = categoria.id

        uow = _make_uow()
        uow.chamados.get_by_id.return_value = chamado
        uow.categorias.get_by_id.return_value = categoria
        uow.usuarios.get_by_id.return_value = solicitante
        uow.comentarios.get_by_chamado.return_value = []
        uow.historico_status.get_by_chamado.return_value = []

        use_case = GetTicketUseCase(unit_of_work=uow)
        result = use_case.execute(chamado.id, solicitante)

        assert result.chamado.id == chamado.id
        assert result.comentarios == []
        assert result.historico == []

    def test_get_ticket_not_found(self):
        """Test retrieving non-existent ticket raises exception."""
        user = UsuarioFactory()
        uow = _make_uow()
        uow.chamados.get_by_id.return_value = None

        use_case = GetTicketUseCase(unit_of_work=uow)

        with pytest.raises(EntityNotFoundException):
            use_case.execute(uuid4(), user)

    def test_get_ticket_unauthorized_solicitante(self):
        """Test that solicitante cannot see another's ticket."""
        owner = UsuarioFactory()
        other = UsuarioFactory()
        chamado = ChamadoFactory(solicitante_id=owner.id)

        uow = _make_uow()
        uow.chamados.get_by_id.return_value = chamado

        use_case = GetTicketUseCase(unit_of_work=uow)

        with pytest.raises(AuthorizationException):
            use_case.execute(chamado.id, other)


class TestListTicketsUseCase:
    """Tests for ListTicketsUseCase."""

    def test_solicitante_sees_only_own(self):
        """Test that solicitante filter is forced to their own ID."""
        user = UsuarioFactory()
        uow = _make_uow()
        uow.chamados.get_paginated_filtered.return_value = ([], 0)

        use_case = ListTicketsUseCase(unit_of_work=uow)
        filters = ChamadoListFilterDTO(page=1, per_page=10)

        use_case.execute(filters, user)

        call_kwargs = uow.chamados.get_paginated_filtered.call_args
        assert (
            call_kwargs.kwargs.get("solicitante_id") == user.id
            or call_kwargs[1].get("solicitante_id") == user.id
        )

    def test_admin_sees_all(self):
        """Test that admin doesn't have forced solicitante filter."""
        admin = UsuarioFactory(admin=True)
        uow = _make_uow()
        uow.chamados.get_paginated_filtered.return_value = ([], 0)

        use_case = ListTicketsUseCase(unit_of_work=uow)
        filters = ChamadoListFilterDTO(page=1, per_page=10)

        use_case.execute(filters, admin)

        call_kwargs = uow.chamados.get_paginated_filtered.call_args
        solicitante_id = call_kwargs.kwargs.get("solicitante_id") or call_kwargs[1].get(
            "solicitante_id"
        )
        assert solicitante_id is None


class TestAssignAttendantUseCase:
    """Tests for AssignAttendantUseCase."""

    def test_assign_success(self):
        """Test successful attendant assignment."""
        admin = UsuarioFactory(admin=True)
        atendente = UsuarioFactory(atendente=True)
        chamado = ChamadoFactory()
        categoria = CategoriaFactory()
        solicitante = UsuarioFactory()
        chamado.categoria_id = categoria.id
        chamado.solicitante_id = solicitante.id

        uow = _make_uow()
        uow.chamados.get_by_id.return_value = chamado
        uow.usuarios.get_by_id.side_effect = lambda uid: (
            atendente if uid == atendente.id else solicitante if uid == solicitante.id else None
        )
        uow.categorias.get_by_id.return_value = categoria

        dto = AtribuirAtendenteDTO(chamado_id=chamado.id, atendente_id=atendente.id)
        use_case = AssignAttendantUseCase(unit_of_work=uow)
        result = use_case.execute(dto, admin)

        assert result.atendente_nome == atendente.nome
        uow.chamados.update.assert_called_once()
        uow.commit.assert_called_once()

    def test_assign_without_permission(self):
        """Test that solicitante cannot assign attendant."""
        solicitante = UsuarioFactory()
        dto = AtribuirAtendenteDTO(chamado_id=uuid4(), atendente_id=uuid4())
        uow = _make_uow()

        use_case = AssignAttendantUseCase(unit_of_work=uow)

        with pytest.raises(AuthorizationException):
            use_case.execute(dto, solicitante)

    def test_assign_inactive_attendant(self):
        """Test that inactive attendant cannot be assigned."""
        admin = UsuarioFactory(admin=True)
        inactive = UsuarioFactory(atendente=True, inativo=True)
        chamado = ChamadoFactory()

        uow = _make_uow()
        uow.chamados.get_by_id.return_value = chamado
        uow.usuarios.get_by_id.return_value = inactive

        dto = AtribuirAtendenteDTO(chamado_id=chamado.id, atendente_id=inactive.id)
        use_case = AssignAttendantUseCase(unit_of_work=uow)

        with pytest.raises(ValidationException):
            use_case.execute(dto, admin)


class TestAddCommentUseCase:
    """Tests for AddCommentUseCase."""

    def test_add_comment_success(self):
        """Test successful comment addition."""
        user = UsuarioFactory()
        chamado = ChamadoFactory(solicitante_id=user.id)

        uow = _make_uow()
        uow.chamados.get_by_id.return_value = chamado
        uow.comentarios.add.return_value = None

        dto = ComentarioCreateDTO(chamado_id=chamado.id, conteudo="Test comment")
        use_case = AddCommentUseCase(unit_of_work=uow)
        result = use_case.execute(dto, user)

        assert result.conteudo == "Test comment"
        uow.comentarios.add.assert_called_once()
        uow.commit.assert_called_once()

    def test_add_comment_closed_ticket(self):
        """Test that commenting on closed ticket raises exception."""
        user = UsuarioFactory()
        chamado = ChamadoFactory(fechado=True, solicitante_id=user.id)

        uow = _make_uow()
        uow.chamados.get_by_id.return_value = chamado

        dto = ComentarioCreateDTO(chamado_id=chamado.id, conteudo="Test")
        use_case = AddCommentUseCase(unit_of_work=uow)

        with pytest.raises(TicketClosedException):
            use_case.execute(dto, user)

    def test_add_comment_empty_content(self):
        """Test that empty comment raises exception."""
        user = UsuarioFactory()

        uow = _make_uow()
        dto = ComentarioCreateDTO(chamado_id=uuid4(), conteudo="   ")
        use_case = AddCommentUseCase(unit_of_work=uow)

        with pytest.raises(ValidationException):
            use_case.execute(dto, user)

    def test_add_comment_unauthorized_solicitante(self):
        """Test that solicitante cannot comment on another's ticket."""
        owner = UsuarioFactory()
        other = UsuarioFactory()
        chamado = ChamadoFactory(solicitante_id=owner.id)

        uow = _make_uow()
        uow.chamados.get_by_id.return_value = chamado

        dto = ComentarioCreateDTO(chamado_id=chamado.id, conteudo="Sneaky comment")
        use_case = AddCommentUseCase(unit_of_work=uow)

        with pytest.raises(AuthorizationException):
            use_case.execute(dto, other)
