from app.ext.db import db
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Categoria(db.Model):
    __tablename__ = 'categorias'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    description: Mapped[str] = mapped_column(db.String(255))
    is_active: Mapped[bool] = mapped_column(db.Boolean, default=True)
