"""Login Use Case."""

from dataclasses import dataclass
from typing import Protocol

from src.application.dtos import LoginDTO, LoginResponseDTO, UsuarioResponseDTO
from src.domain.exceptions import InvalidCredentialsException, UserInactiveException


class IPasswordHasher(Protocol):
    """Interface para serviço de hash de senha."""
    def verify(self, plain_password: str, hashed_password: str) -> bool: ...


@dataclass
class LoginUseCase:
    """
    Use Case para autenticação de usuário.
    
    Responsabilidades:
    - Validar credenciais
    - Verificar se usuário está ativo
    - Retornar dados do usuário autenticado
    """
    
    usuario_repository: "IUsuarioRepository"
    password_hasher: IPasswordHasher
    
    def execute(self, dto: LoginDTO) -> LoginResponseDTO:
        """
        Executa o login.
        
        Args:
            dto: Dados de login
            
        Returns:
            Dados do usuário autenticado
            
        Raises:
            InvalidCredentialsException: Se credenciais inválidas
            UserInactiveException: Se usuário inativo
        """
        email = dto.email.lower().strip()
        
        usuario = self.usuario_repository.get_by_email(email)
        
        if usuario is None:
            raise InvalidCredentialsException()
        
        if not self.password_hasher.verify(dto.senha, usuario.senha_hash):
            raise InvalidCredentialsException()
        
        if not usuario.ativo:
            raise UserInactiveException(email)
        
        return LoginResponseDTO(
            usuario=UsuarioResponseDTO.from_entity(usuario)
        )


from src.domain.interfaces.repositories import IUsuarioRepository
