from typing import TYPE_CHECKING
from app.ext.db import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

if TYPE_CHECKING:
    from .role import Cargo

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('cargos.id'), nullable=False)
    is_active: Mapped[bool] = mapped_column(db.Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.now)

    cargo: Mapped['Cargo'] = relationship(
        'Cargo',
        foreign_keys=[role_id],
    )
