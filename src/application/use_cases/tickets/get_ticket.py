"""Get Ticket Use Case."""

from dataclasses import dataclass
from uuid import UUID

from src.application.dtos import ChamadoResponseDTO, ComentarioResponseDTO
from src.domain.entities import HistoricoStatus, Usuario
from src.domain.enums import PerfilUsuario
from src.domain.exceptions import AuthorizationException, EntityNotFoundException


@dataclass
class TicketDetailDTO:
    """DTO completo de detalhe do chamado."""

    chamado: ChamadoResponseDTO
    comentarios: list[ComentarioResponseDTO]
    historico: list[dict]


@dataclass
class GetTicketUseCase:
    """
    Use Case para obter detalhes de um chamado.

    Inclui comentários e histórico de status.
    """

    unit_of_work: "IUnitOfWork"

    def execute(self, chamado_id: UUID, usuario: Usuario) -> TicketDetailDTO:
        """
        Obtém detalhes do chamado.

        Args:
            chamado_id: ID do chamado
            usuario: Usuário realizando a consulta

        Returns:
            Detalhes completos do chamado

        Raises:
            EntityNotFoundException: Se chamado não existe
            AuthorizationException: Se usuário não tem acesso
        """
        with self.unit_of_work:
            chamado = self.unit_of_work.chamados.get_by_id(chamado_id)
            if not chamado:
                raise EntityNotFoundException("Chamado", chamado_id)

            if usuario.perfil == PerfilUsuario.SOLICITANTE:
                if chamado.solicitante_id != usuario.id:
                    raise AuthorizationException("Você não tem acesso a este chamado")

            categoria = None
            if chamado.categoria_id:
                categoria = self.unit_of_work.categorias.get_by_id(chamado.categoria_id)

            solicitante = None
            if chamado.solicitante_id:
                solicitante = self.unit_of_work.usuarios.get_by_id(chamado.solicitante_id)

            atendente = None
            if chamado.atendente_id:
                atendente = self.unit_of_work.usuarios.get_by_id(chamado.atendente_id)

            comentarios_entities = self.unit_of_work.comentarios.get_by_chamado(
                chamado_id, order_asc=True
            )

            usuarios_cache = {}
            if solicitante:
                usuarios_cache[solicitante.id] = solicitante.nome
            if atendente:
                usuarios_cache[atendente.id] = atendente.nome

            comentarios = []
            for c in comentarios_entities:
                autor_nome = "Desconhecido"
                if c.autor_id:
                    if c.autor_id not in usuarios_cache:
                        autor = self.unit_of_work.usuarios.get_by_id(c.autor_id)
                        usuarios_cache[c.autor_id] = autor.nome if autor else "Desconhecido"
                    autor_nome = usuarios_cache.get(c.autor_id) or "Desconhecido"

                comentarios.append(ComentarioResponseDTO.from_entity(c, autor_nome=autor_nome))

            historico_entities = self.unit_of_work.historico_status.get_by_chamado(
                chamado_id, order_asc=True
            )

            historico = []
            for h in historico_entities:
                alterado_por = "Sistema"
                if h.alterado_por_usuario_id:
                    if h.alterado_por_usuario_id not in usuarios_cache:
                        user = self.unit_of_work.usuarios.get_by_id(h.alterado_por_usuario_id)
                        usuarios_cache[h.alterado_por_usuario_id] = (
                            user.nome if user else "Desconhecido"
                        )
                    alterado_por = usuarios_cache.get(h.alterado_por_usuario_id) or "Sistema"

                historico.append(
                    {
                        "id": str(h.id),
                        "status_anterior": h.status_anterior or "Novo",
                        "status_novo": h.status_novo,
                        "motivo": h.motivo,
                        "alterado_por": alterado_por,
                        "alterado_em": h.alterado_em.isoformat(),
                    }
                )

            transicoes = chamado.transicoes_disponiveis(usuario.perfil, usuario.id)

        chamado_dto = ChamadoResponseDTO.from_entity(
            chamado,
            categoria_nome=categoria.nome if categoria else None,
            solicitante_nome=solicitante.nome if solicitante else None,
            atendente_nome=atendente.nome if atendente else None,
            transicoes=transicoes,
        )

        return TicketDetailDTO(
            chamado=chamado_dto,
            comentarios=comentarios,
            historico=historico,
        )


from src.domain.interfaces.repositories import IUnitOfWork
