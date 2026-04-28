"""API v1 namespaces."""

from src.presentation.api.v1.auth import auth_ns
from src.presentation.api.v1.tickets import tickets_ns
from src.presentation.api.v1.categories import categories_ns
from src.presentation.api.v1.users import users_ns

__all__ = [
    "auth_ns",
    "tickets_ns", 
    "categories_ns",
    "users_ns",
]
