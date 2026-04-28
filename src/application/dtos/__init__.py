"""Application DTOs - Data Transfer Objects."""

from src.application.dtos.usuario_dto import (
    UsuarioCreateDTO,
    UsuarioUpdateDTO,
    UsuarioResponseDTO,
    LoginDTO,
    LoginResponseDTO,
)
from src.application.dtos.chamado_dto import (
    ChamadoCreateDTO,
    ChamadoUpdateDTO,
    ChamadoResponseDTO,
    ChamadoListFilterDTO,
    AlterarStatusDTO,
    AtribuirAtendenteDTO,
)
from src.application.dtos.categoria_dto import (
    CategoriaCreateDTO,
    CategoriaUpdateDTO,
    CategoriaResponseDTO,
)
from src.application.dtos.comentario_dto import (
    ComentarioCreateDTO,
    ComentarioResponseDTO,
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
