from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column


class Cargo(db.Model):
    __tablename__ = 'cargos'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(60), nullable=False)
    description: Mapped[str] = mapped_column(db.Text)
    is_active: Mapped[bool] = mapped_column(db.Boolean, default=True)