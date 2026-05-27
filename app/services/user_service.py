from app.extensions import db
from app.models.category import Categoria
from app.models.role import Cargo
from app.models.user import Usuario

from . import STAFF_ROLES
from .exceptions import NotFoundError, ValidationError


def list_users():
    return Usuario.query.order_by(Usuario.name).all()


def list_staff():
    return (
        Usuario.query.join(Cargo)
        .filter(Cargo.name.in_(STAFF_ROLES))
        .order_by(Usuario.name)
        .all()
    )


def list_staff_for_area(area_id):
    """Staff (atendentes/admins) de uma área — alvos válidos de atribuição."""
    if area_id is None:
        return []
    return (
        Usuario.query.join(Cargo)
        .filter(Cargo.name.in_(STAFF_ROLES), Usuario.area_id == area_id)
        .order_by(Usuario.name)
        .all()
    )


def get_user(user_id):
    user = db.session.get(Usuario, user_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    return user


def update_user(user_id, name=None, role_id=None, area_id=None, is_active=None):
    user = get_user(user_id)
    if name is not None:
        user.name = name
    if role_id is not None:
        if db.session.get(Cargo, role_id) is None:
            raise ValidationError("Cargo informado não existe.")
        user.role_id = role_id
    if area_id is not None:
        if db.session.get(Categoria, area_id) is None:
            raise ValidationError("Área informada não existe.")
        user.area_id = area_id
    if is_active is not None:
        user.is_active = is_active
    db.session.commit()
    return user
