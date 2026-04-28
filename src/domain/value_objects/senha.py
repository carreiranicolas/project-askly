"""Password Value Object."""

from dataclasses import dataclass

from src.domain.exceptions import ValidationException


@dataclass(frozen=True)
class Senha:
    """
    Value Object para senha (texto plano antes de hash).

    Realiza validação de força da senha.
    NUNCA armazene este objeto - use apenas para validação
    antes de gerar o hash.
    """

    value: str

    MIN_LENGTH: int = 6
    MAX_LENGTH: int = 128

    def __post_init__(self):
        """Valida a senha."""
        if not self.value:
            raise ValidationException("Senha é obrigatória", field="senha")

        if len(self.value) < self.MIN_LENGTH:
            raise ValidationException(
                f"A senha deve ter pelo menos {self.MIN_LENGTH} caracteres", field="senha"
            )

        if len(self.value) > self.MAX_LENGTH:
            raise ValidationException(
                f"A senha deve ter no máximo {self.MAX_LENGTH} caracteres", field="senha"
            )

    def __str__(self) -> str:
        return "********"

    def __repr__(self) -> str:
        return "Senha(********)"

    @classmethod
    def validar_confirmacao(cls, senha: str, confirmacao: str) -> None:
        """
        Valida se senha e confirmação são iguais.

        Args:
            senha: Senha digitada
            confirmacao: Confirmação da senha

        Raises:
            ValidationException: Se não conferem
        """
        if senha != confirmacao:
            raise ValidationException("As senhas não conferem", field="confirmar_senha")
