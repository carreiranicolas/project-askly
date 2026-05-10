from app.ext.db import db
from typing import List, TYPE_CHECKING , Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user import Usuario
    from app.models.category import Categoria

class Chamado(db.Model):
    __tablename__ = 'chamados'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(db.String(150), nullable=False)
    descricao: Mapped[str] = mapped_column(db.Text, nullable=False)
    prioridade: Mapped[str] = mapped_column(db.String(20), default='media')
    status: Mapped[str] = mapped_column(db.String(30), default='Aberto')
    solicitante_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    atendente_id: Mapped[Optional[int]] = mapped_column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    categoria_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=datetime.now)
    atualizado_em: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)

    solicitante: Mapped[List["Usuario"]] = relationship(
        "Usuario",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )
    atendente: Mapped[List["Usuario"]] = relationship(
        "Usuario",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )