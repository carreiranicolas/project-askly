"""Ticket Repository implementation."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.domain.entities import Chamado
from src.domain.enums import Prioridade, StatusChamado
from src.domain.interfaces.repositories import IChamadoRepository
from src.infrastructure.persistence.sqlalchemy.models import ChamadoModel


class ChamadoRepository(IChamadoRepository):
    """SQLAlchemy implementation of IChamadoRepository."""

    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, entity_id: UUID) -> Chamado | None:
        model = self._session.get(ChamadoModel, entity_id)
        return model.to_entity() if model else None

    def get_all(self) -> list[Chamado]:
        models = self._session.query(ChamadoModel).all()
        return [m.to_entity() for m in models]

    def add(self, entity: Chamado) -> Chamado:
        model = ChamadoModel.from_entity(entity)
        self._session.add(model)
        self._session.flush()
        return entity

    def update(self, entity: Chamado) -> Chamado:
        model = self._session.get(ChamadoModel, entity.id)
        if model:
            model.update_from_entity(entity)
            self._session.flush()
        return entity

    def delete(self, entity_id: UUID) -> bool:
        model = self._session.get(ChamadoModel, entity_id)
        if model:
            self._session.delete(model)
            return True
        return False

    def exists(self, entity_id: UUID) -> bool:
        return bool(
            self._session.query(
                self._session.query(ChamadoModel).filter_by(id=entity_id).exists()
            ).scalar()
        )

    def count(self) -> int:
        return self._session.query(ChamadoModel).count()

    def get_by_solicitante(
        self, solicitante_id: UUID, page: int = 1, per_page: int = 10
    ) -> tuple[list[Chamado], int]:
        query = self._session.query(ChamadoModel).filter(
            ChamadoModel.solicitante_id == solicitante_id
        )

        total = query.count()
        models = (
            query.order_by(ChamadoModel.criado_em.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return [m.to_entity() for m in models], total

    def get_by_atendente(
        self, atendente_id: UUID, page: int = 1, per_page: int = 10
    ) -> tuple[list[Chamado], int]:
        query = self._session.query(ChamadoModel).filter(ChamadoModel.atendente_id == atendente_id)

        total = query.count()
        models = (
            query.order_by(ChamadoModel.criado_em.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return [m.to_entity() for m in models], total

    def get_fila_atendimento(
        self,
        page: int = 1,
        per_page: int = 10,
        status: StatusChamado | None = None,
        prioridade: Prioridade | None = None,
        categoria_id: UUID | None = None,
    ) -> tuple[list[Chamado], int]:
        query = self._session.query(ChamadoModel).filter(
            ChamadoModel.status_atual != StatusChamado.FECHADO.value
        )

        if status:
            query = query.filter(ChamadoModel.status_atual == status.value)
        if prioridade:
            query = query.filter(ChamadoModel.prioridade == prioridade.value)
        if categoria_id:
            query = query.filter(ChamadoModel.categoria_id == categoria_id)

        total = query.count()
        models = (
            query.order_by(ChamadoModel.criado_em.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return [m.to_entity() for m in models], total

    def get_paginated_filtered(
        self,
        page: int = 1,
        per_page: int = 10,
        status: StatusChamado | None = None,
        prioridade: Prioridade | None = None,
        categoria_id: UUID | None = None,
        solicitante_id: UUID | None = None,
        atendente_id: UUID | None = None,
        data_inicio: datetime | None = None,
        data_fim: datetime | None = None,
    ) -> tuple[list[Chamado], int]:
        query = self._session.query(ChamadoModel)

        if status:
            query = query.filter(ChamadoModel.status_atual == status.value)
        if prioridade:
            query = query.filter(ChamadoModel.prioridade == prioridade.value)
        if categoria_id:
            query = query.filter(ChamadoModel.categoria_id == categoria_id)
        if solicitante_id:
            query = query.filter(ChamadoModel.solicitante_id == solicitante_id)
        if atendente_id:
            query = query.filter(ChamadoModel.atendente_id == atendente_id)
        if data_inicio:
            query = query.filter(ChamadoModel.criado_em >= data_inicio)
        if data_fim:
            query = query.filter(ChamadoModel.criado_em <= data_fim)

        total = query.count()
        models = (
            query.order_by(ChamadoModel.criado_em.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return [m.to_entity() for m in models], total

    def count_by_status(self) -> dict[StatusChamado, int]:
        results = (
            self._session.query(ChamadoModel.status_atual, func.count(ChamadoModel.id))
            .group_by(ChamadoModel.status_atual)
            .all()
        )

        return {StatusChamado(status): count for status, count in results}

    def count_by_categoria(self) -> dict[UUID, int]:
        results = (
            self._session.query(ChamadoModel.categoria_id, func.count(ChamadoModel.id))
            .group_by(ChamadoModel.categoria_id)
            .all()
        )

        return {cat_id: count for cat_id, count in results if cat_id is not None}

    def get_abertos_sem_atendente(self) -> list[Chamado]:
        models = (
            self._session.query(ChamadoModel)
            .filter(
                ChamadoModel.status_atual == StatusChamado.ABERTO.value,
                ChamadoModel.atendente_id.is_(None),
            )
            .order_by(ChamadoModel.criado_em)
            .all()
        )

        return [m.to_entity() for m in models]
