"""Add Comment Use Case."""

from dataclasses import dataclass

from src.application.dtos import ComentarioCreateDTO, ComentarioResponseDTO
from src.domain.entities import Usuario, Comentario
from src.domain.enums import PerfilUsuario
from src.domain.exceptions import (
    EntityNotFoundException, 
    AuthorizationException,
    ValidationException,
    TicketClosedException,
)


@dataclass
class AddCommentUseCase:
    """
    Use Case para adicionar comentário a um chamado.
    """
    
    unit_of_work: "IUnitOfWork"
    
    def execute(
        self, 
        dto: ComentarioCreateDTO, 
        usuario: Usuario
    ) -> ComentarioResponseDTO:
        """
        Adiciona comentário ao chamado.
        
        Args:
            dto: Dados do comentário
            usuario: Usuário autor do comentário
            
        Returns:
            Dados do comentário criado
            
        Raises:
            EntityNotFoundException: Se chamado não existe
            AuthorizationException: Se usuário não tem acesso
            ValidationException: Se comentário vazio
            TicketClosedException: Se chamado está fechado
        """
        if not dto.conteudo or not dto.conteudo.strip():
            raise ValidationException(
                "O comentário não pode estar vazio",
                field="conteudo"
            )
        
        with self.unit_of_work:
            chamado = self.unit_of_work.chamados.get_by_id(dto.chamado_id)
            if not chamado:
                raise EntityNotFoundException("Chamado", dto.chamado_id)
            
            if chamado.is_fechado:
                raise TicketClosedException(str(dto.chamado_id))
            
            if usuario.perfil == PerfilUsuario.SOLICITANTE:
                if chamado.solicitante_id != usuario.id:
                    raise AuthorizationException(
                        "Você não tem acesso a este chamado"
                    )
            
            comentario = Comentario(
                chamado_id=dto.chamado_id,
                autor_id=usuario.id,
                conteudo=dto.conteudo.strip(),
            )
            
            self.unit_of_work.comentarios.add(comentario)
            self.unit_of_work.commit()
        
        return ComentarioResponseDTO.from_entity(
            comentario,
            autor_nome=usuario.nome
        )


from src.domain.interfaces.repositories import IUnitOfWork
