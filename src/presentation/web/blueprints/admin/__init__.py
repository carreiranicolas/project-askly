"""Admin blueprint."""

from flask import Blueprint

admin_bp = Blueprint('web.admin', __name__, template_folder='../../templates/admin')

from src.presentation.web.blueprints.admin import routes  # noqa
