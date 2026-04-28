"""Status History Repository implementation."""

from uuid import UUID

from sqlalchemy.orm import Session

from src.domain.entities import HistoricoStatus
from src.domain.interfaces.repositories import IHistoricoStatusRepository
from src.infrastructure.persistence.sqlalchemy.models import HistoricoStatusModel


class HistoricoStatusRepository(IHistoricoStatusRepository):
    """SQLAlchemy implementation of IHistoricoStatusRepository."""
    
    def __init__(self, session: Session):
        self._session = session
    
    def get_by_id(self, entity_id: UUID) -> HistoricoStatus | None:
        model = self._session.get(HistoricoStatusModel, entity_id)
        return model.to_entity() if model else None
    
    def get_all(self) -> list[HistoricoStatus]:
        models = self._session.query(HistoricoStatusModel).all()
        return [m.to_entity() for m in models]
    
    def add(self, entity: HistoricoStatus) -> HistoricoStatus:
        model = HistoricoStatusModel.from_entity(entity)
        self._session.add(model)
        self._session.flush()
        return entity
    
    def update(self, entity: HistoricoStatus) -> HistoricoStatus:
        return entity
    
    def delete(self, entity_id: UUID) -> bool:
        return False
    
    def exists(self, entity_id: UUID) -> bool:
        return self._session.query(
            self._session.query(HistoricoStatusModel).filter_by(id=entity_id).exists()
        ).scalar()
    
    def count(self) -> int:
        return self._session.query(HistoricoStatusModel).count()
    
    def get_by_chamado(
        self,
        chamado_id: UUID,
        order_asc: bool = True
    ) -> list[HistoricoStatus]:
        query = self._session.query(HistoricoStatusModel).filter(
            HistoricoStatusModel.chamado_id == chamado_id
        )
        
        if order_asc:
            query = query.order_by(HistoricoStatusModel.alterado_em.asc())
        else:
            query = query.order_by(HistoricoStatusModel.alterado_em.desc())
        
        return [m.to_entity() for m in query.all()]
    
    def get_ultimo_by_chamado(self, chamado_id: UUID) -> HistoricoStatus | None:
        model = self._session.query(HistoricoStatusModel).filter(
            HistoricoStatusModel.chamado_id == chamado_id
        ).order_by(HistoricoStatusModel.alterado_em.desc()).first()
        
        return model.to_entity() if model else None
    
    def count_by_chamado(self, chamado_id: UUID) -> int:
        return self._session.query(HistoricoStatusModel).filter(
            HistoricoStatusModel.chamado_id == chamado_id
        ).count()
    
    def get_by_usuario(self, usuario_id: UUID) -> list[HistoricoStatus]:
        models = self._session.query(HistoricoStatusModel).filter(
            HistoricoStatusModel.alterado_por_usuario_id == usuario_id
        ).order_by(HistoricoStatusModel.alterado_em.desc()).all()
        return [m.to_entity() for m in models]
