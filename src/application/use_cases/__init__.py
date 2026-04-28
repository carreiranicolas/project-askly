"""Application Use Cases."""

from src.application.use_cases.auth.login import LoginUseCase
from src.application.use_cases.auth.register import RegisterUseCase
from src.application.use_cases.tickets.create_ticket import CreateTicketUseCase
from src.application.use_cases.tickets.change_status import ChangeStatusUseCase
from src.application.use_cases.tickets.assign_attendant import AssignAttendantUseCase
from src.application.use_cases.tickets.list_tickets import ListTicketsUseCase
from src.application.use_cases.tickets.get_ticket import GetTicketUseCase
from src.application.use_cases.tickets.add_comment import AddCommentUseCase
from src.application.use_cases.categories.create_category import CreateCategoryUseCase
from src.application.use_cases.categories.list_categories import ListCategoriesUseCase
from src.application.use_cases.users.list_users import ListUsersUseCase
from src.application.use_cases.users.change_profile import ChangeProfileUseCase

__all__ = [
    # Auth
    "LoginUseCase",
    "RegisterUseCase",
    # Tickets
    "CreateTicketUseCase",
    "ChangeStatusUseCase",
    "AssignAttendantUseCase",
    "ListTicketsUseCase",
    "GetTicketUseCase",
    "AddCommentUseCase",
    # Categories
    "CreateCategoryUseCase",
    "ListCategoriesUseCase",
    # Users
    "ListUsersUseCase",
    "ChangeProfileUseCase",
]
