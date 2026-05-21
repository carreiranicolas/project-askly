from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length

def get_users():
    from app.models.user import Usuario
    return Usuario.query.order_by(Usuario.name).all()

def get_priorities():
    from app.models.priority import Prioridade
    return Prioridade.query.order_by(Prioridade.name).all()

def get_categories():
    from app.models.category import Categoria
    return Categoria.query.order_by(Categoria.name).all()


class RegistrarChamado(FlaskForm):
    requester = QuerySelectField(
        'Usuário Solicitante',
        query_factory=get_users,
        allow_blank=False,
        get_label='name',
        validators=[DataRequired()]
    )

    requester_email = StringField('Email do Solicitante', render_kw={'readonly': True, 'placeholder': 'Adicione um Usuário Solicitante'})
    requester_role = StringField('Cargo do Solicitante', render_kw={'readonly': True, 'placeholder': 'Adicione um Usuário Solicitante'})

    category = QuerySelectField(
        'Categoria',
        query_factory=get_categories,
        allow_blank=False,
        get_label='name',
        validators=[DataRequired()])

    priority = QuerySelectField(
        'Prioridade do Chamado',
        query_factory=get_priorities,
        allow_blank=False,
        get_label='name',
        validators=[DataRequired()]
    )


    title = StringField('Título do Chamado', validators=[DataRequired(), Length(min=2, max=150)])

    description = TextAreaField('Descrição do Chamado', validators=[DataRequired()])

    submit = SubmitField('Registrar Chamado')