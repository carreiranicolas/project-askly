"""Category Repository implementation."""

from uuid import UUID

from sqlalchemy.orm import Session

from src.domain.entities import Categoria
from src.domain.interfaces.repositories import ICategoriaRepository
from src.infrastructure.persistence.sqlalchemy.models import CategoriaModel


class CategoriaRepository(ICategoriaRepository):
    """SQLAlchemy implementation of ICategoriaRepository."""

    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, entity_id: UUID) -> Categoria | None:
        model = self._session.get(CategoriaModel, entity_id)
        return model.to_entity() if model else None

    def get_all(self) -> list[Categoria]:
        models = self._session.query(CategoriaModel).all()
        return [m.to_entity() for m in models]

    def add(self, entity: Categoria) -> Categoria:
        model = CategoriaModel.from_entity(entity)
        self._session.add(model)
        self._session.flush()
        return entity

    def update(self, entity: Categoria) -> Categoria:
        model = self._session.get(CategoriaModel, entity.id)
        if model:
            model.update_from_entity(entity)
            self._session.flush()
        return entity

    def delete(self, entity_id: UUID) -> bool:
        model = self._session.get(CategoriaModel, entity_id)
        if model:
            self._session.delete(model)
            return True
        return False

    def exists(self, entity_id: UUID) -> bool:
        return self._session.query(
            self._session.query(CategoriaModel).filter_by(id=entity_id).exists()
        ).scalar()

    def count(self) -> int:
        return self._session.query(CategoriaModel).count()

    def get_by_nome(self, nome: str) -> Categoria | None:
        model = (
            self._session.query(CategoriaModel).filter(CategoriaModel.nome == nome.strip()).first()
        )
        return model.to_entity() if model else None

    def nome_exists(self, nome: str, exclude_id: UUID | None = None) -> bool:
        query = self._session.query(CategoriaModel).filter(CategoriaModel.nome == nome.strip())
        if exclude_id:
            query = query.filter(CategoriaModel.id != exclude_id)
        return query.first() is not None

    def get_ativas(self) -> list[Categoria]:
        models = (
            self._session.query(CategoriaModel)
            .filter(CategoriaModel.ativa == True)
            .order_by(CategoriaModel.nome)
            .all()
        )
        return [m.to_entity() for m in models]

    def get_all_ordered(self) -> list[Categoria]:
        models = self._session.query(CategoriaModel).order_by(CategoriaModel.nome).all()
        return [m.to_entity() for m in models]
