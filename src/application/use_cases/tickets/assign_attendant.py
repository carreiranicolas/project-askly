"""Assign Attendant Use Case."""

from dataclasses import dataclass

from src.application.dtos import AtribuirAtendenteDTO, ChamadoResponseDTO
from src.domain.entities import Usuario
from src.domain.enums import PerfilUsuario
from src.domain.exceptions import (
    EntityNotFoundException, 
    AuthorizationException,
    ValidationException,
)


@dataclass
class AssignAttendantUseCase:
    """
    Use Case para atribuição de atendente a chamado.
    """
    
    unit_of_work: "IUnitOfWork"
    
    def execute(
        self, 
        dto: AtribuirAtendenteDTO, 
        usuario_atual: Usuario
    ) -> ChamadoResponseDTO:
        """
        Atribui atendente ao chamado.
        
        Args:
            dto: Dados da atribuição
            usuario_atual: Usuário realizando a atribuição
            
        Returns:
            Dados do chamado atualizado
            
        Raises:
            EntityNotFoundException: Se chamado ou atendente não existe
            AuthorizationException: Se usuário não tem permissão
            ValidationException: Se atendente não é válido
        """
        if not usuario_atual.pode_atribuir_chamados():
            raise AuthorizationException(
                "Você não tem permissão para atribuir chamados",
                required_permission="assign_ticket"
            )
        
        with self.unit_of_work:
            chamado = self.unit_of_work.chamados.get_by_id(dto.chamado_id)
            if not chamado:
                raise EntityNotFoundException("Chamado", dto.chamado_id)
            
            atendente = self.unit_of_work.usuarios.get_by_id(dto.atendente_id)
            if not atendente:
                raise EntityNotFoundException("Usuário", dto.atendente_id)
            
            if atendente.perfil not in (PerfilUsuario.ATENDENTE, PerfilUsuario.ADMIN):
                raise ValidationException(
                    "O usuário selecionado não é um atendente",
                    field="atendente_id"
                )
            
            if not atendente.ativo:
                raise ValidationException(
                    "O atendente selecionado está inativo",
                    field="atendente_id"
                )
            
            chamado.atribuir_atendente(dto.atendente_id)
            
            self.unit_of_work.chamados.update(chamado)
            self.unit_of_work.commit()
            
            categoria = self.unit_of_work.categorias.get_by_id(chamado.categoria_id)
            solicitante = self.unit_of_work.usuarios.get_by_id(chamado.solicitante_id)
        
        transicoes = chamado.transicoes_disponiveis(usuario_atual.perfil, usuario_atual.id)
        
        return ChamadoResponseDTO.from_entity(
            chamado,
            categoria_nome=categoria.nome if categoria else None,
            solicitante_nome=solicitante.nome if solicitante else None,
            atendente_nome=atendente.nome,
            transicoes=transicoes
        )


from src.domain.interfaces.repositories import IUnitOfWork
