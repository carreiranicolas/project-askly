"""Category SQLAlchemy Model."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities import Categoria
from src.infrastructure.persistence.sqlalchemy.models.base import db

if TYPE_CHECKING:
    from src.infrastructure.persistence.sqlalchemy.models.chamado_model import ChamadoModel


class CategoriaModel(db.Model):  # type: ignore[name-defined, misc]
    """SQLAlchemy model for categorias table."""

    __tablename__ = "categorias"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    chamados: Mapped[list["ChamadoModel"]] = relationship(
        "ChamadoModel", back_populates="categoria", lazy="dynamic"
    )

    def to_entity(self) -> Categoria:
        """Convert to domain entity."""
        return Categoria(
            id=self.id,
            nome=self.nome,
            descricao=self.descricao,
            ativa=self.ativa,
            criado_em=self.criado_em,
        )

    @classmethod
    def from_entity(cls, entity: Categoria) -> "CategoriaModel":
        """Create model from domain entity."""
        return cls(
            id=entity.id,
            nome=entity.nome,
            descricao=entity.descricao,
            ativa=entity.ativa,
            criado_em=entity.criado_em,
        )

    def update_from_entity(self, entity: Categoria) -> None:
        """Update model from entity."""
        self.nome = entity.nome
        self.descricao = entity.descricao
        self.ativa = entity.ativa

    def __repr__(self) -> str:
        return f"<CategoriaModel {self.nome}>"
