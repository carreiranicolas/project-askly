"""Ticket (Chamado) domain entity."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID

from src.domain.entities.base import Entity
from src.domain.enums import StatusChamado, Prioridade, PerfilUsuario
from src.domain.exceptions import (
    InvalidStatusTransitionException,
    TicketClosedException,
    ReopenDeadlineExpiredException,
    AuthorizationException,
)


@dataclass
class Chamado(Entity):
    """
    Entidade principal do sistema - Chamado/Ticket.
    
    Representa uma solicitação de suporte/serviço com seu ciclo de vida.
    
    Attributes:
        titulo: Título resumido do chamado
        descricao: Descrição detalhada do problema/solicitação
        prioridade: Nível de prioridade
        status_atual: Status atual no ciclo de vida
        categoria_id: ID da categoria do chamado
        solicitante_id: ID do usuário que abriu o chamado
        atendente_id: ID do atendente responsável (pode ser None)
        resolvido_em: Data/hora da resolução
        fechado_em: Data/hora do fechamento
        criado_em: Data/hora de criação
        atualizado_em: Data/hora da última atualização
    """
    
    titulo: str = ""
    descricao: str = ""
    prioridade: Prioridade = Prioridade.MEDIA
    status_atual: StatusChamado = StatusChamado.ABERTO
    categoria_id: UUID | None = None
    solicitante_id: UUID | None = None
    atendente_id: UUID | None = None
    resolvido_em: datetime | None = None
    fechado_em: datetime | None = None
    criado_em: datetime = field(default_factory=Entity.now)
    atualizado_em: datetime = field(default_factory=Entity.now)
    
    # Constante de negócio: prazo para reabertura em dias
    PRAZO_REABERTURA_DIAS: int = 3
    
    def __post_init__(self):
        """Normaliza os campos de texto."""
        if self.titulo:
            self.titulo = self.titulo.strip()
        if self.descricao:
            self.descricao = self.descricao.strip()
    
    @property
    def is_fechado(self) -> bool:
        return self.status_atual == StatusChamado.FECHADO
    
    @property
    def is_resolvido(self) -> bool:
        return self.status_atual == StatusChamado.RESOLVIDO
    
    @property
    def is_ativo(self) -> bool:
        return self.status_atual.is_ativo()
    
    @property
    def tem_atendente(self) -> bool:
        return self.atendente_id is not None
    
    def pode_reabrir(self) -> bool:
        """
        Verifica se o chamado pode ser reaberto.
        
        Regra de negócio: reabertura permitida até 3 dias após resolução.
        """
        if self.status_atual != StatusChamado.RESOLVIDO:
            return False
        if not self.resolvido_em:
            return False
        
        limite = self.resolvido_em + timedelta(days=self.PRAZO_REABERTURA_DIAS)
        return Entity.now() <= limite
    
    def validar_transicao(
        self, 
        novo_status: StatusChamado, 
        perfil_usuario: PerfilUsuario,
        usuario_id: UUID
    ) -> None:
        """
        Valida se a transição de status é permitida.
        
        Args:
            novo_status: Status de destino
            perfil_usuario: Perfil do usuário realizando a operação
            usuario_id: ID do usuário realizando a operação
            
        Raises:
            TicketClosedException: Se o chamado está fechado
            InvalidStatusTransitionException: Se a transição não é permitida
            AuthorizationException: Se o usuário não tem permissão
            ReopenDeadlineExpiredException: Se o prazo de reabertura expirou
        """
        if self.is_fechado:
            raise TicketClosedException(str(self.id))
        
        if novo_status not in self.status_atual.transicoes_permitidas():
            raise InvalidStatusTransitionException(
                self.status_atual.value,
                novo_status.value
            )
        
        roles_permitidos = self.status_atual.roles_permitidos_transicao(novo_status)
        if perfil_usuario not in roles_permitidos:
            raise AuthorizationException(
                f"Perfil '{perfil_usuario.value}' não pode realizar esta transição",
                required_permission=f"transition_{self.status_atual.value}_to_{novo_status.value}"
            )
        
        if perfil_usuario == PerfilUsuario.SOLICITANTE:
            if self.solicitante_id != usuario_id:
                raise AuthorizationException(
                    "Você só pode alterar seus próprios chamados"
                )
        
        if (self.status_atual == StatusChamado.RESOLVIDO and 
            novo_status == StatusChamado.EM_ATENDIMENTO):
            if not self.pode_reabrir():
                raise ReopenDeadlineExpiredException(self.PRAZO_REABERTURA_DIAS)
    
    def alterar_status(
        self,
        novo_status: StatusChamado,
        perfil_usuario: PerfilUsuario,
        usuario_id: UUID
    ) -> None:
        """
        Altera o status do chamado após validação.
        
        IMPORTANTE: Esta operação DEVE ser acompanhada de registro
        em HistoricoStatus (responsabilidade do Use Case).
        """
        self.validar_transicao(novo_status, perfil_usuario, usuario_id)
        
        self.status_atual = novo_status
        self.atualizado_em = Entity.now()
        
        if novo_status == StatusChamado.RESOLVIDO:
            self.resolvido_em = Entity.now()
        elif novo_status == StatusChamado.FECHADO:
            self.fechado_em = Entity.now()
        elif novo_status == StatusChamado.EM_ATENDIMENTO and self.is_resolvido:
            self.resolvido_em = None
    
    def atribuir_atendente(self, atendente_id: UUID) -> None:
        """Atribui um atendente ao chamado."""
        if self.is_fechado:
            raise TicketClosedException(str(self.id))
        self.atendente_id = atendente_id
        self.atualizado_em = Entity.now()
    
    def remover_atendente(self) -> None:
        """Remove o atendente do chamado."""
        self.atendente_id = None
        self.atualizado_em = Entity.now()
    
    def transicoes_disponiveis(self, perfil: PerfilUsuario, usuario_id: UUID) -> list[StatusChamado]:
        """
        Retorna lista de status disponíveis para transição.
        
        Args:
            perfil: Perfil do usuário
            usuario_id: ID do usuário
            
        Returns:
            Lista de StatusChamado permitidos
        """
        disponiveis = []
        for status in self.status_atual.transicoes_permitidas():
            try:
                self.validar_transicao(status, perfil, usuario_id)
                disponiveis.append(status)
            except Exception:
                continue
        return disponiveis
    
    def __repr__(self) -> str:
        return f"Chamado(id={self.id}, titulo='{self.titulo[:30]}...', status={self.status_atual.value})"
