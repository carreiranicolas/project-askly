"""Base entity class."""

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


@dataclass
class Entity(ABC):
    """
    Classe base para todas as entidades de domínio.

    Implementa padrão de identidade por ID e equality baseada em ID.
    """

    id: UUID = field(default_factory=uuid4)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @staticmethod
    def generate_id() -> UUID:
        """Gera um novo UUID."""
        return uuid4()

    @staticmethod
    def now() -> datetime:
        """Retorna datetime atual com timezone UTC."""
        return datetime.now(timezone.utc)
