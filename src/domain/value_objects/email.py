"""Email Value Object."""

import re
from dataclasses import dataclass

from src.domain.exceptions import ValidationException


@dataclass(frozen=True)
class Email:
    """
    Value Object para email.
    
    Imutável e validado na criação.
    """
    
    value: str
    
    EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    
    def __post_init__(self):
        """Valida e normaliza o email."""
        if not self.value:
            raise ValidationException("Email é obrigatório", field="email")
        
        normalized = self.value.lower().strip()
        
        if not self.EMAIL_REGEX.match(normalized):
            raise ValidationException("Email inválido", field="email")
        
        object.__setattr__(self, "value", normalized)
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Email):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other.lower().strip()
        return False
    
    def __hash__(self) -> int:
        return hash(self.value)
