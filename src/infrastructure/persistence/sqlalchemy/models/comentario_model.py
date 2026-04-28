"""Comment SQLAlchemy Model."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.sqlalchemy.models.base import db
from src.domain.entities import Comentario

if TYPE_CHECKING:
    from src.infrastructure.persistence.sqlalchemy.models.chamado_model import ChamadoModel
    from src.infrastructure.persistence.sqlalchemy.models.usuario_model import UsuarioModel


class ComentarioModel(db.Model):
    """SQLAlchemy model for comentarios table."""
    
    __tablename__ = "comentarios"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    chamado_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chamados.id"),
        nullable=False,
        index=True
    )
    autor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True
    )
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    
    chamado: Mapped["ChamadoModel"] = relationship(
        "ChamadoModel",
        back_populates="comentarios"
    )
    autor: Mapped["UsuarioModel"] = relationship(
        "UsuarioModel",
        back_populates="comentarios"
    )
    
    def to_entity(self) -> Comentario:
        """Convert to domain entity."""
        return Comentario(
            id=self.id,
            chamado_id=self.chamado_id,
            autor_id=self.autor_id,
            conteudo=self.conteudo,
            criado_em=self.criado_em,
        )
    
    @classmethod
    def from_entity(cls, entity: Comentario) -> "ComentarioModel":
        """Create model from domain entity."""
        return cls(
            id=entity.id,
            chamado_id=entity.chamado_id,
            autor_id=entity.autor_id,
            conteudo=entity.conteudo,
            criado_em=entity.criado_em,
        )
    
    def __repr__(self) -> str:
        return f"<ComentarioModel {self.id}>"
