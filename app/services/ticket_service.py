from datetime import datetime, timedelta

from sqlalchemy import false, or_

from app.extensions import db
from app.models.category import Categoria
from app.models.commentary import Comentario
from app.models.history import HistoricoStatus
from app.models.priority import Prioridade
from app.models.ticket import Chamado, StatusEnum
from app.models.user import Usuario

from . import ROLE_ADMIN, ROLE_ATENDENTE, is_staff, role_of
from .exceptions import NotFoundError, PermissionDenied, ValidationError

# Estados terminais/ativos para a máquina de transições.
_CLOSED_OR_RESOLVED = (StatusEnum.RESOLVIDO, StatusEnum.FECHADO, StatusEnum.CANCELADO)
_ACTIVE = [s for s in StatusEnum if s not in _CLOSED_OR_RESOLVED]


def parse_status(value):
    """Aceita o nome do enum (EM_ATENDIMENTO) ou o rótulo (Em Atendimento)."""
    if isinstance(value, StatusEnum):
        return value
    if value is None:
        raise ValidationError("Status é obrigatório.")
    key = str(value).strip()
    if key in StatusEnum.__members__:
        return StatusEnum[key]
    for status in StatusEnum:
        if status.value.lower() == key.lower():
            return status
    raise ValidationError(f"Status inválido: {value}.")


def allowed_transitions(current):
    """Transições válidas a partir do status atual (máquina de estados)."""
    if current == StatusEnum.CANCELADO:
        return []
    if current == StatusEnum.FECHADO:
        return [StatusEnum.ABERTO]  # reabertura
    if current == StatusEnum.RESOLVIDO:
        return [StatusEnum.FECHADO, StatusEnum.ABERTO]
    # Estados ativos: podem ir para outro estado ativo, resolver ou cancelar.
    return [s for s in _ACTIVE if s != current] + [
        StatusEnum.RESOLVIDO,
        StatusEnum.CANCELADO,
    ]


# ------------------------------- SLA -------------------------------
def sla_deadline(ticket):
    if ticket.priority is None or ticket.priority.sla_hours is None:
        return None
    return ticket.created_at + timedelta(hours=ticket.priority.sla_hours)


def is_overdue(ticket):
    deadline = sla_deadline(ticket)
    if deadline is None or ticket.status in _CLOSED_OR_RESOLVED:
        return False
    now = datetime.now(deadline.tzinfo) if deadline.tzinfo else datetime.now()
    return now > deadline


# ----------------------------- Consultas -----------------------------
def _can_view(user, ticket):
    role = role_of(user)
    if role == ROLE_ADMIN:
        return True
    if ticket.requester_id == user.id:
        return True
    if role == ROLE_ATENDENTE:
        return ticket.category_id == user.area_id or ticket.assignee_id == user.id
    return False


def tickets_query(user, tipo=None, categoria_id=None, q=None):
    """Query de chamados já com RBAC + filtros (para listar/paginar/contar)."""
    role = role_of(user)
    query = Chamado.query

    if role == ROLE_ADMIN:
        pass  # admin vê todos
    elif role == ROLE_ATENDENTE:
        if user.area_id is None:
            return query.filter(false())  # sem área => nada
        query = query.filter(Chamado.category_id == user.area_id)
    else:
        query = query.filter(Chamado.requester_id == user.id)

    if tipo == "atribuidos":
        query = query.filter(Chamado.assignee_id == user.id)
    elif tipo == "meus":
        query = query.filter(Chamado.requester_id == user.id)
    if categoria_id:
        query = query.filter(Chamado.category_id == categoria_id)
    if q and q.strip():
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(Chamado.title.ilike(like), Chamado.description.ilike(like))
        )
    return query.order_by(Chamado.created_at.desc())


def list_tickets(user, tipo=None, categoria_id=None, q=None):
    return tickets_query(user, tipo=tipo, categoria_id=categoria_id, q=q).all()


def get_ticket(user, ticket_id):
    ticket = db.session.get(Chamado, ticket_id)
    if ticket is None:
        raise NotFoundError("Chamado não encontrado.")
    if not _can_view(user, ticket):
        raise PermissionDenied("Você não tem acesso a este chamado.")
    return ticket


def create_ticket(user, title, description, category_id, priority_id):
    if not title or not title.strip():
        raise ValidationError("O título é obrigatório.")
    if not description or not description.strip():
        raise ValidationError("A descrição é obrigatória.")
    if db.session.get(Categoria, category_id) is None:
        raise ValidationError("Área informada não existe.")
    if db.session.get(Prioridade, priority_id) is None:
        raise ValidationError("Prioridade informada não existe.")

    ticket = Chamado(
        title=title,
        description=description,
        category_id=category_id,
        priority_id=priority_id,
        requester_id=user.id,
        status=StatusEnum.ABERTO,
    )
    db.session.add(ticket)
    db.session.commit()
    return ticket


def change_status(user, ticket_id, new_status, motivo=None):
    ticket = get_ticket(user, ticket_id)
    target = parse_status(new_status)

    if ticket.status == target:
        raise ValidationError("O chamado já está nesse status.")

    if role_of(user) not in (ROLE_ATENDENTE, ROLE_ADMIN):
        # Solicitante só pode cancelar o próprio chamado.
        if not (ticket.requester_id == user.id and target == StatusEnum.CANCELADO):
            raise PermissionDenied("Você não pode alterar o status deste chamado.")

    if target not in allowed_transitions(ticket.status):
        raise ValidationError(
            f"Transição inválida: de '{ticket.status.value}' para '{target.value}'."
        )

    previous = ticket.status
    ticket.status = target
    # Auditoria obrigatória: toda mudança de status gera histórico (com motivo).
    db.session.add(
        HistoricoStatus(
            ticket_id=ticket.id,
            previous_status=previous.value,
            new_status=target.value,
            motivo=(motivo.strip() if motivo and motivo.strip() else None),
            changed_by_id=user.id,
        )
    )
    db.session.commit()
    return ticket


def assign_ticket(actor, ticket_id, assignee_id):
    if not is_staff(actor):
        raise PermissionDenied(
            "Apenas atendentes ou administradores podem atribuir chamados."
        )
    # get_ticket aplica o RBAC de área (atendente só atua na própria área).
    ticket = get_ticket(actor, ticket_id)

    assignee = db.session.get(Usuario, assignee_id)
    if assignee is None:
        raise ValidationError("Usuário atribuído não existe.")
    if not is_staff(assignee):
        raise ValidationError("Só é possível atribuir a atendentes ou administradores.")

    ticket.assignee_id = assignee_id
    db.session.commit()
    return ticket


def list_history(user, ticket_id):
    ticket = get_ticket(user, ticket_id)
    return (
        HistoricoStatus.query.filter_by(ticket_id=ticket.id)
        .order_by(HistoricoStatus.created_at)
        .all()
    )


def list_comments(user, ticket_id):
    ticket = get_ticket(user, ticket_id)
    return (
        Comentario.query.filter_by(ticket_id=ticket.id)
        .order_by(Comentario.created_at)
        .all()
    )


def add_comment(user, ticket_id, content):
    ticket = get_ticket(user, ticket_id)
    if not content or not content.strip():
        raise ValidationError("O comentário não pode ser vazio.")
    comment = Comentario(content=content, ticket_id=ticket.id, author_id=user.id)
    db.session.add(comment)
    db.session.commit()
    return comment


# ----------------------------- Dashboard -----------------------------
def dashboard_metrics(user):
    tickets = tickets_query(user).all()
    by_status = {}
    by_area = {}
    overdue = 0
    for t in tickets:
        by_status[t.status.value] = by_status.get(t.status.value, 0) + 1
        area = t.category.name if t.category else "—"
        by_area[area] = by_area.get(area, 0) + 1
        if is_overdue(t):
            overdue += 1
    return {
        "total": len(tickets),
        "abertos": sum(1 for t in tickets if t.status == StatusEnum.ABERTO),
        "resolvidos": sum(1 for t in tickets if t.status == StatusEnum.RESOLVIDO),
        "fechados": sum(1 for t in tickets if t.status == StatusEnum.FECHADO),
        "atrasados": overdue,
        "por_status": sorted(by_status.items(), key=lambda kv: kv[0]),
        "por_area": sorted(by_area.items(), key=lambda kv: kv[0]),
    }
