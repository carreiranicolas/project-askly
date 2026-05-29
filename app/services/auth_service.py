from email_validator import EmailNotValidError, validate_email

from app.extensions import db
from app.models.category import Categoria
from app.models.role import Cargo
from app.models.user import Usuario

from . import ROLE_SOLICITANTE
from .exceptions import AuthError, ConflictError, ValidationError

PASSWORD_MIN_LENGTH = 8


def _default_role_id():
    """Cargo do cadastro público: Solicitante.

    Quem se cadastra abre e acompanha os próprios chamados. A promoção a
    Atendente (técnico de uma área) ou Admin é feita por um administrador
    no painel `/admin/usuarios` — manter Atendente como default expandiria
    indevidamente a visibilidade do recém-cadastrado para toda a área.
    """
    cargo = Cargo.query.filter_by(name=ROLE_SOLICITANTE).first()
    if cargo is None:
        raise ValidationError("Cargo padrão indisponível. Rode o seed para popular os cargos.")
    return cargo.id


def _validate_registration(name, email, password):
    if not name or len(name.strip()) < 2:
        raise ValidationError("Nome deve ter ao menos 2 caracteres.")
    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        raise ValidationError("E-mail inválido.")
    if not password or len(password) < PASSWORD_MIN_LENGTH:
        raise ValidationError(f"A senha deve ter ao menos {PASSWORD_MIN_LENGTH} caracteres.")


def authenticate(email, password):
    user = Usuario.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise AuthError("E-mail ou senha incorretos.")
    if not user.is_active:
        raise AuthError("Sua conta está desativada. Procure um administrador.")
    return user


def register(name, email, password, role_id=None, area_id=None):
    _validate_registration(name, email, password)
    if Usuario.query.filter_by(email=email).first():
        raise ConflictError("Este e-mail já está cadastrado no sistema.")
    if role_id is None:
        role_id = _default_role_id()
    elif db.session.get(Cargo, role_id) is None:
        raise ValidationError("Cargo informado não existe.")
    if area_id is not None and db.session.get(Categoria, area_id) is None:
        raise ValidationError("Área informada não existe.")

    user = Usuario(name=name, email=email, role_id=role_id, area_id=area_id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def change_password(user, current_password, new_password):
    if not user.check_password(current_password):
        raise AuthError("Senha atual incorreta.")
    if not new_password or len(new_password) < PASSWORD_MIN_LENGTH:
        raise ValidationError(f"A nova senha deve ter ao menos {PASSWORD_MIN_LENGTH} caracteres.")
    user.set_password(new_password)
    db.session.commit()
    return user
