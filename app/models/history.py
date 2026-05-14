from typing import TYPE_CHECKING
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
    ticket_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('chamados.id'), nullable=False)
    previous_status: Mapped[str] = mapped_column(db.String(30), nullable=False)
    new_status: Mapped[str] = mapped_column(db.String(30), nullable=False)
    changed_by_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=datetime.now, nullable=False)

    chamado: Mapped["Chamado"] = relationship(
        'Chamado',
        foreign_keys=[ticket_id],
    )
    changed_by: Mapped["Usuario"] = relationship(
        'Usuario',
        foreign_keys=[changed_by_id],
    )
