"""Application DTOs - Data Transfer Objects."""

from src.application.dtos.categoria_dto import (
    CategoriaCreateDTO,
    CategoriaResponseDTO,
    CategoriaUpdateDTO,
)
from src.application.dtos.chamado_dto import (
    AlterarStatusDTO,
    AtribuirAtendenteDTO,
    ChamadoCreateDTO,
    ChamadoListFilterDTO,
    ChamadoResponseDTO,
    ChamadoUpdateDTO,
)
from src.application.dtos.comentario_dto import (
    ComentarioCreateDTO,
    ComentarioResponseDTO,
)
from src.application.dtos.usuario_dto import (
    LoginDTO,
    LoginResponseDTO,
    UsuarioCreateDTO,
    UsuarioResponseDTO,
    UsuarioUpdateDTO,
)

__all__ = [
    # Usuario
    "UsuarioCreateDTO",
    "UsuarioUpdateDTO",
    "UsuarioResponseDTO",
    "LoginDTO",
    "LoginResponseDTO",
    # Chamado
    "ChamadoCreateDTO",
    "ChamadoUpdateDTO",
    "ChamadoResponseDTO",
    "ChamadoListFilterDTO",
    "AlterarStatusDTO",
    "AtribuirAtendenteDTO",
    # Categoria
    "CategoriaCreateDTO",
    "CategoriaUpdateDTO",
    "CategoriaResponseDTO",
    # Comentario
    "ComentarioCreateDTO",
    "ComentarioResponseDTO",
]
