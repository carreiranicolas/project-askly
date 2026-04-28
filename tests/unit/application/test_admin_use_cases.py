"""Tests for admin use cases: ChangeProfile, ListUsers, CreateCategory."""

from unittest.mock import MagicMock, Mock
from uuid import uuid4

import pytest

from src.application.dtos import CategoriaCreateDTO
from src.application.use_cases import (
    ChangeProfileUseCase,
    CreateCategoryUseCase,
    ListUsersUseCase,
)
from src.domain.enums import PerfilUsuario
from src.domain.exceptions import AuthorizationException, ValidationException
from tests.fixtures.factories import CategoriaFactory, UsuarioFactory


def _make_uow():
    """Create a MagicMock UoW with context manager support."""
    uow = MagicMock()
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=False)
    return uow


class TestChangeProfileUseCase:
    """Tests for ChangeProfileUseCase."""

    def test_change_profile_success(self):
        """Test successful profile change by admin."""
        admin = UsuarioFactory(admin=True)
        target = UsuarioFactory()

        uow = _make_uow()
        uow.usuarios.get_by_id.return_value = target

        use_case = ChangeProfileUseCase(unit_of_work=uow)
        result = use_case.execute(target.id, PerfilUsuario.ATENDENTE, admin)

        assert result.perfil == "atendente"
        uow.usuarios.update.assert_called_once()
        uow.commit.assert_called_once()

    def test_change_profile_non_admin_rejected(self):
        """Test that non-admin cannot change profiles."""
        solicitante = UsuarioFactory()
        uow = _make_uow()

        use_case = ChangeProfileUseCase(unit_of_work=uow)

        with pytest.raises(AuthorizationException):
            use_case.execute(uuid4(), PerfilUsuario.ADMIN, solicitante)

    def test_admin_cannot_demote_self(self):
        """Test that admin cannot demote their own profile."""
        admin = UsuarioFactory(admin=True)

        uow = _make_uow()
        uow.usuarios.get_by_id.return_value = admin

        use_case = ChangeProfileUseCase(unit_of_work=uow)

        with pytest.raises(ValidationException):
            use_case.execute(admin.id, PerfilUsuario.SOLICITANTE, admin)

    def test_change_profile_user_not_found(self):
        """Test changing profile for non-existent user."""
        admin = UsuarioFactory(admin=True)

        uow = _make_uow()
        uow.usuarios.get_by_id.return_value = None

        use_case = ChangeProfileUseCase(unit_of_work=uow)

        from src.domain.exceptions import EntityNotFoundException

        with pytest.raises(EntityNotFoundException):
            use_case.execute(uuid4(), PerfilUsuario.ATENDENTE, admin)


class TestListUsersUseCase:
    """Tests for ListUsersUseCase."""

    def test_list_users_admin_success(self):
        """Test admin can list users."""
        admin = UsuarioFactory(admin=True)

        uow = _make_uow()
        uow.usuarios.get_paginated.return_value = ([admin], 1)

        use_case = ListUsersUseCase(unit_of_work=uow)
        result = use_case.execute(admin, page=1, per_page=10)

        assert result.total == 1
        assert len(result.items) == 1

    def test_list_users_non_admin_rejected(self):
        """Test that non-admin cannot list users."""
        solicitante = UsuarioFactory()
        uow = _make_uow()

        use_case = ListUsersUseCase(unit_of_work=uow)

        with pytest.raises(AuthorizationException):
            use_case.execute(solicitante, page=1, per_page=10)


class TestCreateCategoryUseCase:
    """Tests for CreateCategoryUseCase."""

    def test_create_category_success(self):
        """Test successful category creation."""
        admin = UsuarioFactory(admin=True)

        uow = _make_uow()
        uow.categorias.nome_exists.return_value = False
        uow.categorias.add.return_value = None

        dto = CategoriaCreateDTO(nome="TI - Nova", descricao="Descrição")
        use_case = CreateCategoryUseCase(unit_of_work=uow)
        result = use_case.execute(dto, admin)

        assert result.nome == "TI - Nova"
        uow.categorias.add.assert_called_once()
        uow.commit.assert_called_once()

    def test_create_category_duplicate_name(self):
        """Test creating category with existing name raises exception."""
        admin = UsuarioFactory(admin=True)

        uow = _make_uow()
        uow.categorias.nome_exists.return_value = True

        dto = CategoriaCreateDTO(nome="Existing", descricao="Desc")
        use_case = CreateCategoryUseCase(unit_of_work=uow)

        with pytest.raises(ValidationException):
            use_case.execute(dto, admin)

    def test_create_category_non_admin_rejected(self):
        """Test that non-admin cannot create categories."""
        solicitante = UsuarioFactory()
        uow = _make_uow()

        dto = CategoriaCreateDTO(nome="Test", descricao="Desc")
        use_case = CreateCategoryUseCase(unit_of_work=uow)

        with pytest.raises(AuthorizationException):
            use_case.execute(dto, solicitante)

    def test_create_category_empty_name(self):
        """Test creating category with empty name raises exception."""
        admin = UsuarioFactory(admin=True)
        uow = _make_uow()

        dto = CategoriaCreateDTO(nome="   ", descricao="Desc")
        use_case = CreateCategoryUseCase(unit_of_work=uow)

        with pytest.raises(ValidationException):
            use_case.execute(dto, admin)
