"""Register Use Case."""

from dataclasses import dataclass
from typing import Protocol

from src.application.dtos import UsuarioCreateDTO, UsuarioResponseDTO
from src.domain.entities import Usuario
from src.domain.enums import PerfilUsuario
from src.domain.value_objects import Email, Senha
from src.domain.exceptions import UserAlreadyExistsException


class IPasswordHasher(Protocol):
    """Interface para serviço de hash de senha."""
    def hash(self, password: str) -> str: ...


@dataclass
class RegisterUseCase:
    """
    Use Case para registro de novo usuário.
    
    Responsabilidades:
    - Validar dados de entrada
    - Verificar unicidade do email
    - Criar hash da senha
    - Persistir usuário
    """
    
    usuario_repository: "IUsuarioRepository"
    unit_of_work: "IUnitOfWork"
    password_hasher: IPasswordHasher
    
    def execute(self, dto: UsuarioCreateDTO) -> UsuarioResponseDTO:
        """
        Executa o registro.
        
        Args:
            dto: Dados do novo usuário
            
        Returns:
            Dados do usuário criado
            
        Raises:
            ValidationException: Se dados inválidos
            UserAlreadyExistsException: Se email já existe
        """
        email = Email(dto.email)
        senha = Senha(dto.senha)
        Senha.validar_confirmacao(dto.senha, dto.confirmar_senha)
        
        if self.usuario_repository.email_exists(email.value):
            raise UserAlreadyExistsException(email.value)
        
        usuario = Usuario(
            nome=dto.nome.strip(),
            email=email.value,
            senha_hash=self.password_hasher.hash(senha.value),
            perfil=PerfilUsuario.SOLICITANTE,  # Sempre solicitante no registro público
            ativo=True,
        )
        
        with self.unit_of_work:
            self.unit_of_work.usuarios.add(usuario)
            self.unit_of_work.commit()
        
        return UsuarioResponseDTO.from_entity(usuario)


from src.domain.interfaces.repositories import IUsuarioRepository, IUnitOfWork
