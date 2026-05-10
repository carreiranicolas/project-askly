from app.ext.db import db
from sql_alchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)
    tipo: Mapped[str] = mapped_column(db.String(20), default='solicitante')  
    ativo: Mapped[bool] = mapped_column(db.Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.now)