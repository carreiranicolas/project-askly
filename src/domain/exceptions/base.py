"""Base domain exceptions."""

from typing import Any


class DomainException(Exception):
    """
    Exceção base para todas as exceções de domínio.

    Attributes:
        message: Mensagem de erro descritiva
        code: Código de erro para identificação
        details: Detalhes adicionais do erro
    """

    def __init__(
        self, message: str, code: str = "DOMAIN_ERROR", details: dict[str, Any] | None = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Converte a exceção para dicionário (útil para APIs)."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class EntityNotFoundException(DomainException):
    """Exceção para quando uma entidade não é encontrada."""

    def __init__(self, entity_name: str, entity_id: Any = None, message: str | None = None):
        self.entity_name = entity_name
        self.entity_id = entity_id
        msg = message or f"{entity_name} não encontrado(a)"
        if entity_id:
            msg = f"{entity_name} com ID '{entity_id}' não encontrado(a)"
        super().__init__(
            message=msg,
            code="ENTITY_NOT_FOUND",
            details={"entity": entity_name, "id": str(entity_id) if entity_id else None},
        )


class ValidationException(DomainException):
    """Exceção para erros de validação de dados."""

    def __init__(
        self, message: str, field: str | None = None, errors: list[dict[str, str]] | None = None
    ):
        self.field = field
        self.errors = errors or []
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={"field": field, "errors": self.errors},
        )


class BusinessRuleViolationException(DomainException):
    """Exceção para violação de regras de negócio."""

    def __init__(self, message: str, rule: str | None = None):
        self.rule = rule
        super().__init__(message=message, code="BUSINESS_RULE_VIOLATION", details={"rule": rule})


class AuthenticationException(DomainException):
    """Exceção para falhas de autenticação."""

    def __init__(self, message: str = "Falha na autenticação"):
        super().__init__(message=message, code="AUTHENTICATION_ERROR")


class AuthorizationException(DomainException):
    """Exceção para falhas de autorização (permissão)."""

    def __init__(
        self,
        message: str = "Você não tem permissão para realizar esta ação",
        required_permission: str | None = None,
    ):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            details={"required_permission": required_permission},
        )
