from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms_sqlalchemy.fields import QuerySelectField

def get_roles():
    from app.models.role import Cargo
    return Cargo.query.order_by(Cargo.name).all()

def get_areas():
    from app.models.category import Categoria
    return Categoria.query.filter_by(is_active=True).order_by(Categoria.name).all()

class RegistrarUsuario(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])

    role = QuerySelectField(
        'Cargo do Usuário',
        query_factory=get_roles,
        allow_blank=False,
        get_label='name',
        validators=[DataRequired()]
    )

    area = QuerySelectField(
        'Área',
        query_factory=get_areas,
        allow_blank=False,
        get_label='name',
        validators=[DataRequired()]
    )

    submit = SubmitField('Registrar Novo Usuário')

