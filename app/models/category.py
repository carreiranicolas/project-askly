from app.ext.db import db
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Categoria(db.Model):
    __tablename__ = 'categorias'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True) 
    nome: Mapped[str] = mapped_column(db.String(50), nullable=False)
    descricao: Mapped[str] = mapped_column(db.String(255))
    ativo: Mapped[bool] = mapped_column(db.Boolean, default=True)