from app.ext.db import db
from sqlalchemy.orm import Mapped, mapped_column

class Prioridade(db.Model):
    __tablename__ = 'prioridades'
    __table_args__ = {'extend_existing': True}

    id : Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(25), nullable=False)
    description: Mapped[str] = mapped_column(db.Text)
    sla_hours: Mapped[int] = mapped_column(db.Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(db.Boolean, default=True)