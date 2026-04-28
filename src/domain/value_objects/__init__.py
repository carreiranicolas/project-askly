"""Value Objects - Objetos de valor imutáveis."""

from src.domain.value_objects.email import Email
from src.domain.value_objects.pagination import PaginatedResult, PaginationParams
from src.domain.value_objects.senha import Senha

__all__ = [
    "Email",
    "Senha",
    "PaginationParams",
    "PaginatedResult",
]
