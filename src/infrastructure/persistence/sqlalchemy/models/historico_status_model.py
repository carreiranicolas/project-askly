"""Status History SQLAlchemy Model."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.sqlalchemy.models.base import db
from src.domain.entities import HistoricoStatus

if TYPE_CHECKING:
    from src.infrastructure.persistence.sqlalchemy.models.chamado_model import ChamadoModel
    from src.infrastructure.persistence.sqlalchemy.models.usuario_model import UsuarioModel


class HistoricoStatusModel(db.Model):
    """SQLAlchemy model for historico_status table (audit trail)."""
    
    __tablename__ = "historico_status"
    
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
    alterado_por_usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False
    )
    status_anterior: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status_novo: Mapped[str] = mapped_column(Text, nullable=False)
    motivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    alterado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    
    chamado: Mapped["ChamadoModel"] = relationship(
        "ChamadoModel",
        back_populates="historico"
    )
    alterado_por: Mapped["UsuarioModel"] = relationship("UsuarioModel")
    
    def to_entity(self) -> HistoricoStatus:
        """Convert to domain entity."""
        return HistoricoStatus(
            id=self.id,
            chamado_id=self.chamado_id,
            alterado_por_usuario_id=self.alterado_por_usuario_id,
            status_anterior=self.status_anterior,
            status_novo=self.status_novo,
            motivo=self.motivo,
            alterado_em=self.alterado_em,
        )
    
    @classmethod
    def from_entity(cls, entity: HistoricoStatus) -> "HistoricoStatusModel":
        """Create model from domain entity."""
        return cls(
            id=entity.id,
            chamado_id=entity.chamado_id,
            alterado_por_usuario_id=entity.alterado_por_usuario_id,
            status_anterior=entity.status_anterior,
            status_novo=entity.status_novo,
            motivo=entity.motivo,
            alterado_em=entity.alterado_em,
        )
    
    def __repr__(self) -> str:
        return f"<HistoricoStatusModel {self.status_anterior} -> {self.status_novo}>"
