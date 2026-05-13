from typing import List, Optional, TYPE_CHECKING
from app.ext.db import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

if TYPE_CHECKING:
    from .ticket import Chamado
    from .user import Usuario

class HistoricoStatus(db.Model):
    __tablename__ = 'historico_status'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    id_chamado: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('chamados.id'), nullable=False)
    status_anterior: Mapped[str] = mapped_column(db.String(30), nullable=False)
    status_novo: Mapped[str] = mapped_column(db.String(30), nullable=False)
    id_alterante: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=datetime.now, nullable=False)

    chamado: Mapped[List['Chamado']] = relationship(
        'Chamado',
        back_populates='historico_status',
        cascade="all, delete-orphan",

    )
    alterante: Mapped[List['Usuario']] = relationship(
        'Usuario',
        back_populates='historico_status',
        cascade="all, delete-orphan",
    )