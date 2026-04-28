"""Tests for RegisterUseCase."""

import pytest
from unittest.mock import Mock, MagicMock

from src.application.dtos import UsuarioCreateDTO
from src.application.use_cases import RegisterUseCase
from src.domain.enums import PerfilUsuario
from src.domain.exceptions import UserAlreadyExistsException, ValidationException
from tests.fixtures.factories import UsuarioFactory


class TestRegisterUseCase:
    """Tests for RegisterUseCase."""

    def _make_use_case(self, email_exists=False):
        """Helper to create use case with mocks."""
        repo = Mock()
        repo.email_exists.return_value = email_exists

        uow = MagicMock()
        uow.usuarios.add.return_value = None
        uow.__enter__ = Mock(return_value=uow)
        uow.__exit__ = Mock(return_value=False)

        hasher = Mock()
        hasher.hash.return_value = 'hashed_password'

        use_case = RegisterUseCase(
            usuario_repository=repo,
            unit_of_work=uow,
            password_hasher=hasher,
        )
        return use_case, uow, hasher

    def test_register_success(self):
        """Test successful registration."""
        use_case, uow, hasher = self._make_use_case()

        dto = UsuarioCreateDTO(
            nome='João Silva',
            email='joao@test.com',
            senha='password123',
            confirmar_senha='password123',
        )

        result = use_case.execute(dto)

        assert result.email == 'joao@test.com'
        assert result.perfil == 'solicitante'
        uow.usuarios.add.assert_called_once()
        uow.commit.assert_called_once()
        hasher.hash.assert_called_once_with('password123')

    def test_register_always_creates_solicitante(self):
        """Test that registration always creates solicitante, even if admin is requested."""
        use_case, uow, _ = self._make_use_case()

        dto = UsuarioCreateDTO(
            nome='Hacker',
            email='hacker@test.com',
            senha='password123',
            confirmar_senha='password123',
            perfil=PerfilUsuario.ADMIN,
        )

        result = use_case.execute(dto)
        assert result.perfil == 'solicitante'

    def test_register_duplicate_email(self):
        """Test registration with existing email raises exception."""
        use_case, _, _ = self._make_use_case(email_exists=True)

        dto = UsuarioCreateDTO(
            nome='Test',
            email='existing@test.com',
            senha='password123',
            confirmar_senha='password123',
        )

        with pytest.raises(UserAlreadyExistsException):
            use_case.execute(dto)

    def test_register_short_password(self):
        """Test registration with short password raises ValidationException."""
        use_case, _, _ = self._make_use_case()

        dto = UsuarioCreateDTO(
            nome='Test',
            email='test@test.com',
            senha='12345',
            confirmar_senha='12345',
        )

        with pytest.raises(ValidationException):
            use_case.execute(dto)

    def test_register_password_mismatch(self):
        """Test registration with mismatched passwords raises ValidationException."""
        use_case, _, _ = self._make_use_case()

        dto = UsuarioCreateDTO(
            nome='Test',
            email='test@test.com',
            senha='password123',
            confirmar_senha='different',
        )

        with pytest.raises(ValidationException):
            use_case.execute(dto)
