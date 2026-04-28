"""Ticket-specific domain exceptions."""

from src.domain.exceptions.base import DomainException


class TicketException(DomainException):
    """Exceção base para erros relacionados a chamados."""
    
    def __init__(self, message: str, code: str = "TICKET_ERROR", **kwargs):
        super().__init__(message=message, code=code, **kwargs)


class InvalidStatusTransitionException(TicketException):
    """Exceção para transição de status inválida."""
    
    def __init__(
        self, 
        status_atual: str, 
        status_destino: str,
        motivo: str | None = None
    ):
        self.status_atual = status_atual
        self.status_destino = status_destino
        msg = f"Transição de '{status_atual}' para '{status_destino}' não é permitida"
        if motivo:
            msg = f"{msg}: {motivo}"
        super().__init__(
            message=msg,
            code="INVALID_STATUS_TRANSITION",
            details={
                "status_atual": status_atual,
                "status_destino": status_destino,
                "motivo": motivo,
            }
        )


class TicketClosedException(TicketException):
    """Exceção para operações em chamado fechado."""
    
    def __init__(self, ticket_id: str | None = None):
        msg = "Não é possível realizar esta operação em um chamado fechado"
        super().__init__(
            message=msg,
            code="TICKET_CLOSED",
            details={"ticket_id": ticket_id}
        )


class ReopenDeadlineExpiredException(TicketException):
    """Exceção para prazo de reabertura expirado."""
    
    def __init__(self, dias_limite: int = 3):
        msg = f"O prazo de {dias_limite} dias para reabertura expirou"
        super().__init__(
            message=msg,
            code="REOPEN_DEADLINE_EXPIRED",
            details={"dias_limite": dias_limite}
        )
