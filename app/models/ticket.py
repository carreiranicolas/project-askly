from app.ext.db import db
from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user import Usuario
    from app.models.category import Categoria

class Chamado(db.Model):
    __tablename__ = 'chamados'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(db.String(150), nullable=False)
    description: Mapped[str] = mapped_column(db.Text, nullable=False)
    priority: Mapped[str] = mapped_column(db.String(20), default='media')
    status: Mapped[str] = mapped_column(db.String(30), default='Aberto')
    requester_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    assignee_id: Mapped[Optional[int]] = mapped_column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    category_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)

    requester: Mapped["Usuario"] = relationship(
        "Usuario",
        foreign_keys=[requester_id],
    )
    assignee: Mapped[Optional["Usuario"]] = relationship(
        "Usuario",
        foreign_keys=[assignee_id],
    )
