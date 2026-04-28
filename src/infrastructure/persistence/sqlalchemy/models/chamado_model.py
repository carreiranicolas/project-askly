"""Ticket SQLAlchemy Model."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.sqlalchemy.models.base import db
from src.domain.entities import Chamado
from src.domain.enums import StatusChamado, Prioridade

if TYPE_CHECKING:
    from src.infrastructure.persistence.sqlalchemy.models.usuario_model import UsuarioModel
    from src.infrastructure.persistence.sqlalchemy.models.categoria_model import CategoriaModel
    from src.infrastructure.persistence.sqlalchemy.models.comentario_model import ComentarioModel
    from src.infrastructure.persistence.sqlalchemy.models.historico_status_model import HistoricoStatusModel


class ChamadoModel(db.Model):
    """SQLAlchemy model for chamados table."""
    
    __tablename__ = "chamados"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    titulo: Mapped[str] = mapped_column(Text, nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    prioridade: Mapped[str] = mapped_column(String(50), nullable=False)
    status_atual: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        default="ABERTO",
        index=True
    )
    
    categoria_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categorias.id"),
        nullable=False,
        index=True
    )
    solicitante_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True
    )
    atendente_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=True,
        index=True
    )
    
    resolvido_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    fechado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    categoria: Mapped["CategoriaModel"] = relationship(
        "CategoriaModel",
        back_populates="chamados"
    )
    solicitante: Mapped["UsuarioModel"] = relationship(
        "UsuarioModel",
        foreign_keys=[solicitante_id],
        back_populates="chamados_criados"
    )
    atendente: Mapped["UsuarioModel | None"] = relationship(
        "UsuarioModel",
        foreign_keys=[atendente_id],
        back_populates="chamados_atendidos"
    )
    comentarios: Mapped[list["ComentarioModel"]] = relationship(
        "ComentarioModel",
        back_populates="chamado",
        lazy="dynamic",
        order_by="ComentarioModel.criado_em"
    )
    historico: Mapped[list["HistoricoStatusModel"]] = relationship(
        "HistoricoStatusModel",
        back_populates="chamado",
        lazy="dynamic",
        order_by="HistoricoStatusModel.alterado_em"
    )
    
    __table_args__ = (
        Index("ix_chamados_prioridade", "prioridade"),
    )
    
    def to_entity(self) -> Chamado:
        """Convert to domain entity."""
        return Chamado(
            id=self.id,
            titulo=self.titulo,
            descricao=self.descricao,
            prioridade=Prioridade(self.prioridade),
            status_atual=StatusChamado(self.status_atual),
            categoria_id=self.categoria_id,
            solicitante_id=self.solicitante_id,
            atendente_id=self.atendente_id,
            resolvido_em=self.resolvido_em,
            fechado_em=self.fechado_em,
            criado_em=self.criado_em,
            atualizado_em=self.atualizado_em,
        )
    
    @classmethod
    def from_entity(cls, entity: Chamado) -> "ChamadoModel":
        """Create model from domain entity."""
        return cls(
            id=entity.id,
            titulo=entity.titulo,
            descricao=entity.descricao,
            prioridade=entity.prioridade.value if isinstance(entity.prioridade, Prioridade) else entity.prioridade,
            status_atual=entity.status_atual.value if isinstance(entity.status_atual, StatusChamado) else entity.status_atual,
            categoria_id=entity.categoria_id,
            solicitante_id=entity.solicitante_id,
            atendente_id=entity.atendente_id,
            resolvido_em=entity.resolvido_em,
            fechado_em=entity.fechado_em,
            criado_em=entity.criado_em,
            atualizado_em=entity.atualizado_em,
        )
    
    def update_from_entity(self, entity: Chamado) -> None:
        """Update model from entity."""
        self.titulo = entity.titulo
        self.descricao = entity.descricao
        self.prioridade = entity.prioridade.value if isinstance(entity.prioridade, Prioridade) else entity.prioridade
        self.status_atual = entity.status_atual.value if isinstance(entity.status_atual, StatusChamado) else entity.status_atual
        self.atendente_id = entity.atendente_id
        self.resolvido_em = entity.resolvido_em
        self.fechado_em = entity.fechado_em
        self.atualizado_em = entity.atualizado_em
    
    def __repr__(self) -> str:
        return f"<ChamadoModel {self.id} - {self.status_atual}>"
