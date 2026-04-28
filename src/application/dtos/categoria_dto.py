"""Category DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class CategoriaCreateDTO:
    """DTO para criação de categoria."""

    nome: str
    descricao: str | None = None


@dataclass
class CategoriaUpdateDTO:
    """DTO para atualização de categoria."""

    id: UUID
    nome: str | None = None
    descricao: str | None = None
    ativa: bool | None = None


@dataclass
class CategoriaResponseDTO:
    """DTO de resposta de categoria."""

    id: UUID
    nome: str
    descricao: str | None
    ativa: bool
    criado_em: datetime

    @classmethod
    def from_entity(cls, categoria) -> "CategoriaResponseDTO":
        """Cria DTO a partir de entidade."""
        return cls(
            id=categoria.id,
            nome=categoria.nome,
            descricao=categoria.descricao,
            ativa=categoria.ativa,
            criado_em=categoria.criado_em,
        )
