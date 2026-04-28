"""Comment Repository implementation."""

from uuid import UUID

from sqlalchemy.orm import Session

from src.domain.entities import Comentario
from src.domain.interfaces.repositories import IComentarioRepository
from src.infrastructure.persistence.sqlalchemy.models import ComentarioModel


class ComentarioRepository(IComentarioRepository):
    """SQLAlchemy implementation of IComentarioRepository."""

    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, entity_id: UUID) -> Comentario | None:
        model = self._session.get(ComentarioModel, entity_id)
        return model.to_entity() if model else None

    def get_all(self) -> list[Comentario]:
        models = self._session.query(ComentarioModel).all()
        return [m.to_entity() for m in models]

    def add(self, entity: Comentario) -> Comentario:
        model = ComentarioModel.from_entity(entity)
        self._session.add(model)
        self._session.flush()
        return entity

    def update(self, entity: Comentario) -> Comentario:
        model = self._session.get(ComentarioModel, entity.id)
        if model:
            model.conteudo = entity.conteudo
            self._session.flush()
        return entity

    def delete(self, entity_id: UUID) -> bool:
        model = self._session.get(ComentarioModel, entity_id)
        if model:
            self._session.delete(model)
            return True
        return False

    def exists(self, entity_id: UUID) -> bool:
        return self._session.query(
            self._session.query(ComentarioModel).filter_by(id=entity_id).exists()
        ).scalar()

    def count(self) -> int:
        return self._session.query(ComentarioModel).count()

    def get_by_chamado(self, chamado_id: UUID, order_asc: bool = True) -> list[Comentario]:
        query = self._session.query(ComentarioModel).filter(
            ComentarioModel.chamado_id == chamado_id
        )

        if order_asc:
            query = query.order_by(ComentarioModel.criado_em.asc())
        else:
            query = query.order_by(ComentarioModel.criado_em.desc())

        return [m.to_entity() for m in query.all()]

    def count_by_chamado(self, chamado_id: UUID) -> int:
        return (
            self._session.query(ComentarioModel)
            .filter(ComentarioModel.chamado_id == chamado_id)
            .count()
        )

    def get_by_autor(self, autor_id: UUID) -> list[Comentario]:
        models = (
            self._session.query(ComentarioModel)
            .filter(ComentarioModel.autor_id == autor_id)
            .order_by(ComentarioModel.criado_em.desc())
            .all()
        )
        return [m.to_entity() for m in models]
