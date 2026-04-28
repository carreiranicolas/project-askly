"""List Tickets Use Case."""

from dataclasses import dataclass

from src.application.dtos import ChamadoListFilterDTO, ChamadoResponseDTO
from src.domain.entities import Usuario
from src.domain.enums import PerfilUsuario
from src.domain.value_objects import PaginatedResult


@dataclass
class ListTicketsUseCase:
    """
    Use Case para listagem de chamados.

    Aplica regras de visibilidade baseadas no perfil:
    - Solicitante: vê apenas seus chamados
    - Atendente/Admin: vê todos os chamados
    """

    unit_of_work: "IUnitOfWork"

    def execute(
        self, filters: ChamadoListFilterDTO, usuario: Usuario
    ) -> PaginatedResult[ChamadoResponseDTO]:
        """
        Lista chamados com filtros.

        Args:
            filters: Filtros de busca
            usuario: Usuário realizando a busca

        Returns:
            Resultado paginado com chamados
        """
        solicitante_id = filters.solicitante_id
        categoria_id = filters.categoria_id

        if usuario.perfil == PerfilUsuario.SOLICITANTE:
            solicitante_id = usuario.id

        if usuario.perfil == PerfilUsuario.ATENDENTE and usuario.categoria_id:
            categoria_id = usuario.categoria_id

        with self.unit_of_work:
            chamados, total = self.unit_of_work.chamados.get_paginated_filtered(
                page=filters.page,
                per_page=filters.per_page,
                status=filters.status,
                prioridade=filters.prioridade,
                categoria_id=categoria_id,
                solicitante_id=solicitante_id,
                atendente_id=filters.atendente_id,
                data_inicio=filters.data_inicio,
                data_fim=filters.data_fim,
            )

            categorias_cache: dict = {}
            usuarios_cache: dict = {}

            def get_categoria_nome(cat_id):
                if cat_id not in categorias_cache:
                    cat = self.unit_of_work.categorias.get_by_id(cat_id)
                    categorias_cache[cat_id] = cat.nome if cat else None
                return categorias_cache[cat_id]

            def get_usuario_nome(user_id):
                if user_id is None:
                    return None
                if user_id not in usuarios_cache:
                    user = self.unit_of_work.usuarios.get_by_id(user_id)
                    usuarios_cache[user_id] = user.nome if user else None
                return usuarios_cache[user_id]

            items = [
                ChamadoResponseDTO.from_entity(
                    chamado,
                    categoria_nome=get_categoria_nome(chamado.categoria_id),
                    solicitante_nome=get_usuario_nome(chamado.solicitante_id),
                    atendente_nome=get_usuario_nome(chamado.atendente_id),
                )
                for chamado in chamados
            ]

        return PaginatedResult(
            items=items,
            total=total,
            page=filters.page,
            per_page=filters.per_page,
        )


from src.domain.interfaces.repositories import IUnitOfWork
