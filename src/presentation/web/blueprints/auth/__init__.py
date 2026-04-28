"""Auth blueprint."""

from flask import Blueprint

auth_bp = Blueprint('web.auth', __name__, template_folder='../../templates/auth')

from src.presentation.web.blueprints.auth import routes  # noqa
