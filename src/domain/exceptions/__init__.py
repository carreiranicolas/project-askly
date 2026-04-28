"""Domain exceptions - Exceções de negócio."""

from src.domain.exceptions.base import (
    AuthenticationException,
    AuthorizationException,
    BusinessRuleViolationException,
    DomainException,
    EntityNotFoundException,
    ValidationException,
)
from src.domain.exceptions.ticket import (
    InvalidStatusTransitionException,
    ReopenDeadlineExpiredException,
    TicketClosedException,
    TicketException,
)
from src.domain.exceptions.user import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserException,
    UserInactiveException,
)

__all__ = [
    # Base
    "DomainException",
    "EntityNotFoundException",
    "ValidationException",
    "BusinessRuleViolationException",
    "AuthenticationException",
    "AuthorizationException",
    # Ticket
    "TicketException",
    "InvalidStatusTransitionException",
    "TicketClosedException",
    "ReopenDeadlineExpiredException",
    # User
    "UserException",
    "UserAlreadyExistsException",
    "UserInactiveException",
    "InvalidCredentialsException",
]
