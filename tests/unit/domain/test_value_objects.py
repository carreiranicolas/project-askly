"""Tests for domain value objects."""

import pytest

from src.domain.exceptions import ValidationException
from src.domain.value_objects import Email, PaginatedResult, PaginationParams, Senha


class TestEmail:
    """Tests for Email value object."""

    def test_valid_email(self):
        """Test valid email creation."""
        email = Email("test@example.com")
        assert email.value == "test@example.com"

    def test_email_normalization(self):
        """Test email is normalized."""
        email = Email("  TEST@EXAMPLE.COM  ")
        assert email.value == "test@example.com"

    def test_invalid_email_raises(self):
        """Test invalid email raises exception."""
        with pytest.raises(ValidationException) as exc:
            Email("invalid-email")
        assert exc.value.field == "email"

    def test_empty_email_raises(self):
        """Test empty email raises exception."""
        with pytest.raises(ValidationException):
            Email("")

    def test_email_equality(self):
        """Test email equality."""
        email1 = Email("test@example.com")
        email2 = Email("TEST@EXAMPLE.COM")

        assert email1 == email2
        assert email1 == "test@example.com"


class TestSenha:
    """Tests for Senha value object."""

    def test_valid_password(self):
        """Test valid password creation."""
        senha = Senha("password123")
        assert senha.value == "password123"

    def test_short_password_raises(self):
        """Test short password raises exception."""
        with pytest.raises(ValidationException) as exc:
            Senha("12345")
        assert exc.value.field == "senha"

    def test_empty_password_raises(self):
        """Test empty password raises exception."""
        with pytest.raises(ValidationException):
            Senha("")

    def test_password_str_hidden(self):
        """Test password string representation is hidden."""
        senha = Senha("secret123")
        assert str(senha) == "********"
        assert "secret" not in repr(senha)

    def test_validar_confirmacao_match(self):
        """Test password confirmation matching."""
        Senha.validar_confirmacao("password123", "password123")

    def test_validar_confirmacao_mismatch(self):
        """Test password confirmation mismatch."""
        with pytest.raises(ValidationException):
            Senha.validar_confirmacao("password123", "different")


class TestPaginationParams:
    """Tests for PaginationParams value object."""

    def test_default_values(self):
        """Test default pagination values."""
        params = PaginationParams()

        assert params.page == 1
        assert params.per_page == 10

    def test_custom_values(self):
        """Test custom pagination values."""
        params = PaginationParams(page=3, per_page=25)

        assert params.page == 3
        assert params.per_page == 25

    def test_negative_page_normalized(self):
        """Test negative page is normalized."""
        params = PaginationParams(page=-1)
        assert params.page == 1

    def test_exceeding_per_page_capped(self):
        """Test per_page exceeding max is capped."""
        params = PaginationParams(per_page=500)
        assert params.per_page == 100

    def test_offset_calculation(self):
        """Test offset calculation."""
        params = PaginationParams(page=3, per_page=10)
        assert params.offset == 20


class TestPaginatedResult:
    """Tests for PaginatedResult value object."""

    def test_pages_calculation(self):
        """Test pages calculation."""
        result = PaginatedResult(items=[], total=25, page=1, per_page=10)
        assert result.pages == 3

    def test_has_next(self):
        """Test has_next."""
        result = PaginatedResult(items=[], total=25, page=1, per_page=10)
        assert result.has_next is True

        result = PaginatedResult(items=[], total=25, page=3, per_page=10)
        assert result.has_next is False

    def test_has_prev(self):
        """Test has_prev."""
        result = PaginatedResult(items=[], total=25, page=1, per_page=10)
        assert result.has_prev is False

        result = PaginatedResult(items=[], total=25, page=2, per_page=10)
        assert result.has_prev is True

    def test_to_dict(self):
        """Test dictionary conversion."""
        result = PaginatedResult(items=["a", "b"], total=10, page=1, per_page=5)
        d = result.to_dict()

        assert d["items"] == ["a", "b"]
        assert d["pagination"]["total"] == 10
        assert d["pagination"]["pages"] == 2
