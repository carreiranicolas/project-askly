from typing import TYPE_CHECKING
from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .ticket import Chamado
    from .user import Usuario

class Comentario(db.Model):
    __tablename__ = 'comentarios'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    content: Mapped[str] = mapped_column(db.Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    ticket_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('chamados.id'), nullable=False)
    author_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    is_active: Mapped[bool] = mapped_column(db.Boolean, default=True)

    chamado: Mapped["Chamado"] = relationship(
        'Chamado',
        foreign_keys=[ticket_id],
        backref = db.backref('comentarios', order_by=created_at.desc(), lazy='dynamic')
    )
    author: Mapped["Usuario"] = relationship(
        'Usuario',
        foreign_keys=[author_id],
        backref = db.backref('comentarios', lazy='dynamic')
    )
