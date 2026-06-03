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

# Estados que param a contagem de SLA (trabalho concluído ou chamado encerrado).
# "Em aberto" no dashboard = qualquer status fora deste conjunto.
_SLA_STOPPED = (
    StatusEnum.AGUARDANDO_APROVACAO,
    StatusEnum.FECHADO,
    StatusEnum.CANCELADO,
)
_ACTIVE = [s for s in StatusEnum if s not in _SLA_STOPPED]


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
    if current == StatusEnum.AGUARDANDO_APROVACAO:
        # Transições só via aprovar/recusar (quem abriu o chamado).
        return []
    # Estados ativos: podem ir para outro estado ativo, enviar para aprovação
    # ou cancelar.
    return [s for s in _ACTIVE if s != current] + [
        StatusEnum.AGUARDANDO_APROVACAO,
        StatusEnum.CANCELADO,
    ]


# ------------------------------- SLA -------------------------------
def sla_deadline(ticket):
    if ticket.priority is None or ticket.priority.sla_hours is None:
        return None
    return ticket.created_at + timedelta(hours=ticket.priority.sla_hours)


def _now_like(dt):
    """datetime.now() ciente do fuso de `dt` (que pode ser naive ou aware)."""
    if dt is not None and dt.tzinfo is not None:
        return datetime.now(dt.tzinfo)
    return datetime.now()


def is_overdue(ticket):
    deadline = sla_deadline(ticket)
    if deadline is None or ticket.status in _SLA_STOPPED:
        return False
    return _now_like(deadline) > deadline


def sla_remaining_label(ticket):
    """Retorna texto legível do tempo restante/atrasado do SLA."""
    deadline = sla_deadline(ticket)
    if deadline is None:
        return None
    if ticket.status in _SLA_STOPPED:
        return "SLA pausado"
    delta_h = (deadline - _now_like(deadline)).total_seconds() / 3600
    hours = abs(delta_h)
    if hours < 1:
        time_str = f"{int(round(hours * 60))}min"
    elif hours < 24:
        time_str = f"{int(round(hours))}h"
    else:
        days = int(hours // 24)
        rest = int(round(hours % 24))
        time_str = f"{days}d {rest}h" if rest else f"{days}d"
    if delta_h < 0:
        return f"Atrasado há {time_str}"
    return f"Faltam {time_str}"


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

    if tipo == "meus":
        # Chamados que abri: sempre pelo solicitante, em qualquer área.
        # Atendentes/admins também podem abrir chamado para outra área e
        # precisam acompanhar em "Chamados que abri" sem o filtro de área.
        query = query.filter(Chamado.requester_id == user.id)
    elif tipo == "atribuidos":
        query = query.filter(Chamado.assignee_id == user.id)
        if role == ROLE_ATENDENTE:
            if user.area_id is None:
                return query.filter(false())
            query = query.filter(Chamado.category_id == user.area_id)
        # Admin: todos os atribuídos; Solicitante: raro, mas assignee_id basta.
    elif role == ROLE_ADMIN:
        pass  # admin vê todos
    elif role == ROLE_ATENDENTE:
        if user.area_id is None:
            return query.filter(false())  # sem área => nada
        query = query.filter(Chamado.category_id == user.area_id)
    else:
        # Solicitante: lista padrão = só os próprios chamados (qualquer área).
        query = query.filter(Chamado.requester_id == user.id)

    if categoria_id:
        query = query.filter(Chamado.category_id == categoria_id)
    if q and q.strip():
        term = q.strip()
        # Permite buscar por ID (com ou sem #) ou por texto no título/descrição.
        if term.startswith("#"):
            term = term[1:]
        if term.isdigit():
            query = query.filter(Chamado.id == int(term))
        else:
            like = f"%{term}%"
            query = query.filter(or_(Chamado.title.ilike(like), Chamado.description.ilike(like)))
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


TITLE_MIN_LENGTH = 2
TITLE_MAX_LENGTH = 150


def create_ticket(user, title, description, category_id, priority_id):
    title = (title or "").strip()
    description = (description or "").strip()

    if len(title) < TITLE_MIN_LENGTH:
        raise ValidationError(f"O título precisa ter ao menos {TITLE_MIN_LENGTH} caracteres.")
    if len(title) > TITLE_MAX_LENGTH:
        raise ValidationError(f"O título pode ter no máximo {TITLE_MAX_LENGTH} caracteres.")
    if not description:
        raise ValidationError("A descrição é obrigatória.")

    categoria = db.session.get(Categoria, category_id) if category_id else None
    if categoria is None:
        raise ValidationError("Área informada não existe.")
    if not categoria.is_active:
        raise ValidationError("Esta área está inativa e não pode receber novos chamados.")

    prioridade = db.session.get(Prioridade, priority_id) if priority_id else None
    if prioridade is None:
        raise ValidationError("Prioridade informada não existe.")
    if not prioridade.is_active:
        raise ValidationError(
            "Esta prioridade está inativa e não pode ser usada em novos chamados."
        )

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


def _record_transition(user, ticket, target, motivo=None, *, skip_validation=False):
    """Aplica a transição validando a máquina de estados e gera auditoria."""
    if not skip_validation and target not in allowed_transitions(ticket.status):
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


def change_status(user, ticket_id, new_status, motivo=None):
    ticket = get_ticket(user, ticket_id)
    target = parse_status(new_status)

    if ticket.status == target:
        raise ValidationError("O chamado já está nesse status.")

    role = role_of(user)

    if ticket.status == StatusEnum.AGUARDANDO_APROVACAO:
        raise PermissionDenied(
            "Este chamado aguarda aprovação de quem abriu. Use Aprovar ou Recusar."
        )

    if ticket.status == StatusEnum.FECHADO and target == StatusEnum.ABERTO:
        if role != ROLE_ADMIN:
            raise PermissionDenied("Apenas administradores podem reabrir chamados fechados.")

    if role not in (ROLE_ATENDENTE, ROLE_ADMIN):
        # Solicitante só pode cancelar o próprio chamado.
        if not (ticket.requester_id == user.id and target == StatusEnum.CANCELADO):
            raise PermissionDenied("Você não pode alterar o status deste chamado.")

    # Atribuição obrigatória: não se movimenta um chamado sem responsável.
    # O cancelamento é exceção (pode encerrar um chamado ainda não atribuído).
    if ticket.assignee_id is None and target != StatusEnum.CANCELADO:
        raise ValidationError("Atribua um responsável ao chamado antes de alterar o status.")

    _record_transition(user, ticket, target, motivo)
    return ticket


def can_approve(user, ticket):
    """Quem abriu o chamado pode aprovar a solução quando aguarda aprovação."""
    return ticket.status == StatusEnum.AGUARDANDO_APROVACAO and ticket.requester_id == user.id


def _require_pending_approval(user, ticket_id):
    ticket = get_ticket(user, ticket_id)
    if ticket.requester_id != user.id:
        raise PermissionDenied("Apenas quem abriu o chamado pode avaliar a solução.")
    if ticket.status != StatusEnum.AGUARDANDO_APROVACAO:
        raise ValidationError("Este chamado não está aguardando aprovação.")
    return ticket


def approve_resolution(user, ticket_id, motivo=None):
    """Quem abriu o chamado aprova a solução, fechando-o automaticamente."""
    ticket = _require_pending_approval(user, ticket_id)
    _record_transition(
        user,
        ticket,
        StatusEnum.FECHADO,
        motivo=motivo or "Solução aprovada por quem abriu o chamado.",
        skip_validation=True,
    )
    return ticket


def reject_resolution(user, ticket_id, motivo=None):
    """Quem abriu recusa a solução: o chamado reabre para o responsável retomar."""
    ticket = _require_pending_approval(user, ticket_id)
    _record_transition(
        user,
        ticket,
        StatusEnum.ABERTO,
        motivo=motivo or "Solução recusada por quem abriu o chamado.",
        skip_validation=True,
    )
    return ticket


def assign_ticket(actor, ticket_id, assignee_id):
    if not is_staff(actor):
        raise PermissionDenied("Apenas atendentes ou administradores podem atribuir chamados.")
    # get_ticket aplica o RBAC de área (atendente só atua na própria área).
    ticket = get_ticket(actor, ticket_id)

    assignee = db.session.get(Usuario, assignee_id)
    if assignee is None:
        raise ValidationError("Usuário atribuído não existe.")
    if not assignee.is_active:
        raise ValidationError("Não é possível atribuir o chamado a um usuário inativo.")
    if not is_staff(assignee):
        raise ValidationError("Só é possível atribuir a atendentes ou administradores.")
    # Atribuição restrita à área do chamado: o responsável precisa ser da
    # mesma área em que o chamado foi aberto.
    if assignee.area_id != ticket.category_id:
        raise ValidationError("Só é possível atribuir a usuários da área do chamado.")

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
    return Comentario.query.filter_by(ticket_id=ticket.id).order_by(Comentario.created_at).all()


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

    # Admin vê todas as áreas cadastradas (mesmo sem chamados).
    if role_of(user) == ROLE_ADMIN:
        for cat in Categoria.query.filter_by(is_active=True).all():
            by_area[cat.name] = 0

    overdue = 0
    em_aberto = 0
    for t in tickets:
        by_status[t.status.value] = by_status.get(t.status.value, 0) + 1
        area = t.category.name if t.category else "—"
        by_area[area] = by_area.get(area, 0) + 1
        # "Em aberto" = qualquer status que ainda demanda trabalho (todos menos
        # aguardando aprovação, fechado e cancelado).
        if t.status in _ACTIVE:
            em_aberto += 1
        if is_overdue(t):
            overdue += 1
    return {
        "total": len(tickets),
        "abertos": em_aberto,
        "aguardando_aprovacao": sum(
            1 for t in tickets if t.status == StatusEnum.AGUARDANDO_APROVACAO
        ),
        "fechados": sum(1 for t in tickets if t.status == StatusEnum.FECHADO),
        "atrasados": overdue,
        "por_status": sorted(by_status.items(), key=lambda kv: kv[0]),
        "por_area": sorted(by_area.items(), key=lambda kv: kv[0]),
    }


# ------------------------------- SLA -------------------------------
def _humanize_hours(hours):
    """Formata uma quantidade de horas em algo legível: 45min, 6h, 2d 3h."""
    hours = abs(hours)
    if hours < 1:
        return f"{int(round(hours * 60))}min"
    if hours < 24:
        return f"{int(round(hours))}h"
    days = int(hours // 24)
    rest = int(round(hours % 24))
    return f"{days}d {rest}h" if rest else f"{days}d"


def _close_timestamps(ticket_ids):
    """Mapa ticket_id -> instante em que entrou em 'Fechado' (via auditoria)."""
    if not ticket_ids:
        return {}
    rows = HistoricoStatus.query.filter(
        HistoricoStatus.ticket_id.in_(ticket_ids),
        HistoricoStatus.new_status == StatusEnum.FECHADO.value,
    ).all()
    closed_at = {}
    for r in rows:
        if r.ticket_id not in closed_at or r.created_at > closed_at[r.ticket_id]:
            closed_at[r.ticket_id] = r.created_at
    return closed_at


def sla_report(user):
    """Acompanhamento de SLA (escopo por RBAC):

    - `ativos`: chamados em aberto com prazo de SLA correndo;
    - `por_area`: tempo médio de fechamento e cumprimento de SLA por área.
    """
    tickets = tickets_query(user).all()

    ativos = []
    for t in tickets:
        if t.status not in _ACTIVE:
            continue
        deadline = sla_deadline(t)
        overdue = is_overdue(t)
        if deadline is None:
            label = "—"
        else:
            delta_h = (deadline - _now_like(deadline)).total_seconds() / 3600
            label = (
                f"Atrasado há {_humanize_hours(delta_h)}"
                if delta_h < 0
                else f"Faltam {_humanize_hours(delta_h)}"
            )
        ativos.append(
            {
                "ticket": t,
                "deadline": deadline,
                "overdue": overdue,
                "remaining_label": label,
            }
        )
    ativos.sort(key=lambda r: (r["deadline"] is None, r["deadline"] or datetime.max))

    closed = [t for t in tickets if t.status == StatusEnum.FECHADO]
    closed_at = _close_timestamps([t.id for t in closed])

    # Admin vê todas as áreas cadastradas; demais usuários só as que aparecem
    # nos chamados que podem visualizar.
    buckets = {}
    if role_of(user) == ROLE_ADMIN:
        for cat in Categoria.query.filter_by(is_active=True).all():
            buckets[cat.name] = {"count": 0, "hours": 0.0, "within": 0}

    for t in closed:
        area = t.category.name if t.category else "—"
        b = buckets.setdefault(area, {"count": 0, "hours": 0.0, "within": 0})
        end = closed_at.get(t.id) or t.updated_at
        if end is not None:
            b["hours"] += (end - t.created_at).total_seconds() / 3600
        b["count"] += 1
        deadline = sla_deadline(t)
        if deadline is not None and end is not None and end <= deadline:
            b["within"] += 1

    por_area = []
    for area, b in sorted(buckets.items(), key=lambda kv: kv[0]):
        avg = b["hours"] / b["count"] if b["count"] else 0
        por_area.append(
            {
                "area": area,
                "fechados": b["count"],
                "avg_hours": avg,
                "avg_label": _humanize_hours(avg) if b["count"] else "—",
                "sla_compliance": round(b["within"] / b["count"] * 100) if b["count"] else 0,
            }
        )

    return {"ativos": ativos, "por_area": por_area}
