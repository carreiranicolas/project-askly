ROLE_SOLICITANTE = "Solicitante"
ROLE_ATENDENTE = "Atendente"
ROLE_ADMIN = "Admin"

STAFF_ROLES = (ROLE_ATENDENTE, ROLE_ADMIN)


def role_of(user):
    if user is None or user.cargo is None:
        return None
    return user.cargo.name


def is_staff(user):
    return role_of(user) in STAFF_ROLES


def is_admin(user):
    return role_of(user) == ROLE_ADMIN
