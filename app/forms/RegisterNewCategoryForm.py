from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class RegistrarCategoria(FlaskForm):
    name = StringField('Nome da Categoria', validators=[DataRequired(), Length(min=2, max=60)])

    description = TextAreaField('Descrição da Categoria', validators=[Length(max=255)])

    submit = SubmitField('Registrar Nova Categoria de Chamado')