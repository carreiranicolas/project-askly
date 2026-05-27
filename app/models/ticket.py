from app.extensions import db
from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import enum

if TYPE_CHECKING:
    from app.models.user import Usuario
    from app.models.category import Categoria
    from app.models.priority import Prioridade

class StatusEnum(enum.Enum):
    ABERTO = 'Aberto'
    EM_ANALISE = 'Em Análise'
    EM_ATENDIMENTO = 'Em Atendimento'
    ATRIBUIR_TECNICO = 'Atribuir Técnico'
    MUDAR_CATEGORIA = 'Mudar Categoria'
    MUDAR_PRIORIDADE = 'Mudar Prioridade'
    AGUARDANDO_CLIENTE = 'Aguardando Cliente'
    AGUARDANDO_TECNICO = 'Aguardando Técnico'
    AGUARDANDO_PECA = 'Aguardando Peça'
    ATENDIMENTO_AGENDADO = 'Atendimento Agendado'
    RESOLVIDO = 'Resolvido'
    FECHADO = 'Fechado'
    CANCELADO = 'Cancelado'


class Chamado(db.Model):
    __tablename__ = 'chamados'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(db.String(150), nullable=False)
    description: Mapped[str] = mapped_column(db.Text, nullable=False)
    priority_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('prioridades.id'), nullable=False)
    status: Mapped[StatusEnum] = mapped_column(db.Enum(StatusEnum), default=StatusEnum.ABERTO)
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

    category: Mapped["Categoria"] = relationship(
        "Categoria",
        backref='chamados',
        foreign_keys=[category_id]
    )

    priority: Mapped["Prioridade"] = relationship(
        "Prioridade",
        backref='chamados',
        foreign_keys=[priority_id]
    )