from typing import List, Optional, TYPE_CHECKING
from app.ext.db import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

if TYPE_CHECKING:
    from .ticket import Chamado
    from .user import Usuario

class Comentario(db.Model):
    __tablename__ = 'comentarios'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    conteudo: Mapped[str] = mapped_column(db.Text, nullable=False)
    crido_em: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=datetime.now)
    id_chamado: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('chamados.id'), nullable=False)
    id_autor: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    chamado: Mapped[List['Chamado']] = relationship(
        'Chamado',
        back_populates='comentarios',
        cascade="all, delete-orphan",
    )
    autor: Mapped[List['Usuario']] = relationship(
        'Usuario',
        back_populates='comentarios',
        cascade="all, delete-orphan",
    )