"""Domain exceptions - Exceções de negócio."""

from src.domain.exceptions.base import (
    DomainException,
    EntityNotFoundException,
    ValidationException,
    BusinessRuleViolationException,
    AuthenticationException,
    AuthorizationException,
)
from src.domain.exceptions.ticket import (
    TicketException,
    InvalidStatusTransitionException,
    TicketClosedException,
    ReopenDeadlineExpiredException,
)
from src.domain.exceptions.user import (
    UserException,
    UserAlreadyExistsException,
    UserInactiveException,
    InvalidCredentialsException,
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
