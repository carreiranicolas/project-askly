"""Tickets blueprint."""

from flask import Blueprint

tickets_bp = Blueprint('web.tickets', __name__, template_folder='../../templates/tickets')

from src.presentation.web.blueprints.tickets import routes  # noqa
