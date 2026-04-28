"""User-specific domain exceptions."""

from src.domain.exceptions.base import DomainException


class UserException(DomainException):
    """Exceção base para erros relacionados a usuários."""

    def __init__(self, message: str, code: str = "USER_ERROR", **kwargs):
        super().__init__(message=message, code=code, **kwargs)


class UserAlreadyExistsException(UserException):
    """Exceção para quando já existe um usuário com o email."""

    def __init__(self, email: str):
        super().__init__(
            message=f"Já existe um usuário cadastrado com o email '{email}'",
            code="USER_ALREADY_EXISTS",
            details={"email": email},
        )


class UserInactiveException(UserException):
    """Exceção para usuário inativo."""

    def __init__(self, email: str | None = None):
        msg = "Sua conta está desativada. Entre em contato com o administrador."
        super().__init__(message=msg, code="USER_INACTIVE", details={"email": email})


class InvalidCredentialsException(UserException):
    """Exceção para credenciais inválidas."""

    def __init__(self):
        super().__init__(message="Email ou senha inválidos", code="INVALID_CREDENTIALS")
