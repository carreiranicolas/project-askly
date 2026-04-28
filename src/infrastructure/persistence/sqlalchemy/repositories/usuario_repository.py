"""User Repository implementation."""

from uuid import UUID

from sqlalchemy.orm import Session

from src.domain.entities import Usuario
from src.domain.enums import PerfilUsuario
from src.domain.interfaces.repositories import IUsuarioRepository
from src.infrastructure.persistence.sqlalchemy.models import UsuarioModel


class UsuarioRepository(IUsuarioRepository):
    """SQLAlchemy implementation of IUsuarioRepository."""

    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, entity_id: UUID) -> Usuario | None:
        model = self._session.get(UsuarioModel, entity_id)
        return model.to_entity() if model else None

    def get_all(self) -> list[Usuario]:
        models = self._session.query(UsuarioModel).all()
        return [m.to_entity() for m in models]

    def add(self, entity: Usuario) -> Usuario:
        model = UsuarioModel.from_entity(entity)
        self._session.add(model)
        self._session.flush()
        return entity

    def update(self, entity: Usuario) -> Usuario:
        model = self._session.get(UsuarioModel, entity.id)
        if model:
            model.update_from_entity(entity)
            self._session.flush()
        return entity

    def delete(self, entity_id: UUID) -> bool:
        model = self._session.get(UsuarioModel, entity_id)
        if model:
            self._session.delete(model)
            return True
        return False

    def exists(self, entity_id: UUID) -> bool:
        return bool(
            self._session.query(
                self._session.query(UsuarioModel).filter_by(id=entity_id).exists()
            ).scalar()
        )

    def count(self) -> int:
        return self._session.query(UsuarioModel).count()

    def get_by_email(self, email: str) -> Usuario | None:
        model = (
            self._session.query(UsuarioModel)
            .filter(UsuarioModel.email == email.lower().strip())
            .first()
        )
        return model.to_entity() if model else None

    def email_exists(self, email: str, exclude_id: UUID | None = None) -> bool:
        query = self._session.query(UsuarioModel).filter(
            UsuarioModel.email == email.lower().strip()
        )
        if exclude_id:
            query = query.filter(UsuarioModel.id != exclude_id)
        return query.first() is not None

    def get_by_perfil(self, perfil: PerfilUsuario) -> list[Usuario]:
        models = (
            self._session.query(UsuarioModel)
            .filter(UsuarioModel.perfil == perfil.value)
            .order_by(UsuarioModel.nome)
            .all()
        )
        return [m.to_entity() for m in models]

    def get_ativos(self) -> list[Usuario]:
        models = (
            self._session.query(UsuarioModel)
            .filter(UsuarioModel.ativo == True)
            .order_by(UsuarioModel.nome)
            .all()
        )
        return [m.to_entity() for m in models]

    def get_atendentes_ativos(self) -> list[Usuario]:
        models = (
            self._session.query(UsuarioModel)
            .filter(
                UsuarioModel.perfil.in_([PerfilUsuario.ATENDENTE.value, PerfilUsuario.ADMIN.value]),
                UsuarioModel.ativo == True,
            )
            .order_by(UsuarioModel.nome)
            .all()
        )
        return [m.to_entity() for m in models]

    def get_paginated(
        self,
        page: int = 1,
        per_page: int = 10,
        perfil: PerfilUsuario | None = None,
        apenas_ativos: bool = False,
    ) -> tuple[list[Usuario], int]:
        query = self._session.query(UsuarioModel)

        if perfil:
            query = query.filter(UsuarioModel.perfil == perfil.value)
        if apenas_ativos:
            query = query.filter(UsuarioModel.ativo == True)

        total = query.count()

        models = (
            query.order_by(UsuarioModel.nome).offset((page - 1) * per_page).limit(per_page).all()
        )

        return [m.to_entity() for m in models], total
