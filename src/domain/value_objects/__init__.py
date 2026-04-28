"""Value Objects - Objetos de valor imutáveis."""

from src.domain.value_objects.email import Email
from src.domain.value_objects.senha import Senha
from src.domain.value_objects.pagination import PaginationParams, PaginatedResult

__all__ = [
    "Email",
    "Senha",
    "PaginationParams",
    "PaginatedResult",
]
