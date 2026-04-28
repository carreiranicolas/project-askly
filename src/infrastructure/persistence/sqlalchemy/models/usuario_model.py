"""User SQLAlchemy Model."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from flask_login import UserMixin
from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.sqlalchemy.models.base import db
from src.domain.entities import Usuario
from src.domain.enums import PerfilUsuario

if TYPE_CHECKING:
    from src.infrastructure.persistence.sqlalchemy.models.chamado_model import ChamadoModel
    from src.infrastructure.persistence.sqlalchemy.models.comentario_model import ComentarioModel


class UsuarioModel(db.Model, UserMixin):
    """SQLAlchemy model for usuarios table."""
    
    __tablename__ = "usuarios"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        unique=True, 
        index=True
    )
    senha_hash: Mapped[str] = mapped_column(Text, nullable=False)
    perfil: Mapped[str] = mapped_column(String(50), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    chamados_criados: Mapped[list["ChamadoModel"]] = relationship(
        "ChamadoModel",
        foreign_keys="ChamadoModel.solicitante_id",
        back_populates="solicitante",
        lazy="dynamic"
    )
    chamados_atendidos: Mapped[list["ChamadoModel"]] = relationship(
        "ChamadoModel",
        foreign_keys="ChamadoModel.atendente_id",
        back_populates="atendente",
        lazy="dynamic"
    )
    comentarios: Mapped[list["ComentarioModel"]] = relationship(
        "ComentarioModel",
        back_populates="autor",
        lazy="dynamic"
    )
    
    def to_entity(self) -> Usuario:
        """Convert to domain entity."""
        return Usuario(
            id=self.id,
            nome=self.nome,
            email=self.email,
            senha_hash=self.senha_hash,
            perfil=PerfilUsuario(self.perfil),
            ativo=self.ativo,
            criado_em=self.criado_em,
        )
    
    @classmethod
    def from_entity(cls, entity: Usuario) -> "UsuarioModel":
        """Create model from domain entity."""
        return cls(
            id=entity.id,
            nome=entity.nome,
            email=entity.email,
            senha_hash=entity.senha_hash,
            perfil=entity.perfil.value if isinstance(entity.perfil, PerfilUsuario) else entity.perfil,
            ativo=entity.ativo,
            criado_em=entity.criado_em,
        )
    
    def update_from_entity(self, entity: Usuario) -> None:
        """Update model from entity."""
        self.nome = entity.nome
        self.email = entity.email
        self.senha_hash = entity.senha_hash
        self.perfil = entity.perfil.value if isinstance(entity.perfil, PerfilUsuario) else entity.perfil
        self.ativo = entity.ativo
    
    def __repr__(self) -> str:
        return f"<UsuarioModel {self.email}>"
