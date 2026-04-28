"""Pagination Value Objects."""

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class PaginationParams:
    """
    Parâmetros de paginação.

    Attributes:
        page: Número da página (1-indexed)
        per_page: Itens por página
    """

    page: int = 1
    per_page: int = 10

    MAX_PER_PAGE: int = 100

    def __post_init__(self):
        """Valida e normaliza parâmetros."""
        if self.page < 1:
            object.__setattr__(self, "page", 1)

        if self.per_page < 1:
            object.__setattr__(self, "per_page", 10)
        elif self.per_page > self.MAX_PER_PAGE:
            object.__setattr__(self, "per_page", self.MAX_PER_PAGE)

    @property
    def offset(self) -> int:
        """Calcula o offset para queries."""
        return (self.page - 1) * self.per_page

    @property
    def limit(self) -> int:
        """Alias para per_page."""
        return self.per_page


@dataclass
class PaginatedResult(Generic[T]):
    """
    Resultado paginado.

    Attributes:
        items: Lista de itens da página atual
        total: Total de itens (todas as páginas)
        page: Página atual
        per_page: Itens por página
    """

    items: list[T]
    total: int
    page: int
    per_page: int

    @property
    def pages(self) -> int:
        """Total de páginas."""
        if self.total == 0:
            return 1
        return (self.total + self.per_page - 1) // self.per_page

    @property
    def has_next(self) -> bool:
        """Se há próxima página."""
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        """Se há página anterior."""
        return self.page > 1

    @property
    def next_page(self) -> int | None:
        """Número da próxima página."""
        return self.page + 1 if self.has_next else None

    @property
    def prev_page(self) -> int | None:
        """Número da página anterior."""
        return self.page - 1 if self.has_prev else None

    def to_dict(self) -> dict:
        """Converte para dicionário (útil para APIs)."""
        return {
            "items": self.items,
            "pagination": {
                "page": self.page,
                "per_page": self.per_page,
                "total": self.total,
                "pages": self.pages,
                "has_next": self.has_next,
                "has_prev": self.has_prev,
            },
        }
