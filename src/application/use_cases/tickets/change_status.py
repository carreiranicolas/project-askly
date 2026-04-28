"""Change Status Use Case."""

from dataclasses import dataclass
from uuid import UUID

from src.application.dtos import AlterarStatusDTO, ChamadoResponseDTO
from src.domain.entities import Chamado, HistoricoStatus, Usuario
from src.domain.enums import StatusChamado
from src.domain.exceptions import EntityNotFoundException


@dataclass
class ChangeStatusUseCase:
    """
    Use Case para alteração de status de chamado.
    
    CONSTRAINT CRÍTICO: Toda alteração de status DEVE gerar
    registro em historico_status na mesma transação.
    Esta é uma exigência mandatória do contrato.
    """
    
    unit_of_work: "IUnitOfWork"
    
    def execute(
        self, 
        dto: AlterarStatusDTO, 
        usuario: Usuario
    ) -> ChamadoResponseDTO:
        """
        Altera o status do chamado.
        
        Args:
            dto: Dados da alteração
            usuario: Usuário realizando a alteração
            
        Returns:
            Dados do chamado atualizado
            
        Raises:
            EntityNotFoundException: Se chamado não existe
            InvalidStatusTransitionException: Se transição inválida
            AuthorizationException: Se usuário não tem permissão
            ReopenDeadlineExpiredException: Se prazo de reabertura expirou
        """
        with self.unit_of_work:
            chamado = self.unit_of_work.chamados.get_by_id(dto.chamado_id)
            if not chamado:
                raise EntityNotFoundException("Chamado", dto.chamado_id)
            
            status_anterior = chamado.status_atual
            
            chamado.alterar_status(
                novo_status=dto.novo_status,
                perfil_usuario=usuario.perfil,
                usuario_id=usuario.id
            )
            
            self.unit_of_work.chamados.update(chamado)
            
            historico = HistoricoStatus.criar_para_transicao(
                chamado_id=chamado.id,
                usuario_id=usuario.id,
                status_anterior=status_anterior,
                status_novo=dto.novo_status,
                motivo=dto.motivo
            )
            self.unit_of_work.historico_status.add(historico)
            
            self.unit_of_work.commit()
            
            categoria = self.unit_of_work.categorias.get_by_id(chamado.categoria_id)
            solicitante = self.unit_of_work.usuarios.get_by_id(chamado.solicitante_id)
            atendente = None
            if chamado.atendente_id:
                atendente = self.unit_of_work.usuarios.get_by_id(chamado.atendente_id)
        
        transicoes = chamado.transicoes_disponiveis(usuario.perfil, usuario.id)
        
        return ChamadoResponseDTO.from_entity(
            chamado,
            categoria_nome=categoria.nome if categoria else None,
            solicitante_nome=solicitante.nome if solicitante else None,
            atendente_nome=atendente.nome if atendente else None,
            transicoes=transicoes
        )


from src.domain.interfaces.repositories import IUnitOfWork
