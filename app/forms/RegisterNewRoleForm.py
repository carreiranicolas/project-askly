from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class RegistrarCargo(FlaskForm):
    name = StringField('Nome do Cargo', validators=[DataRequired(), Length(min=2, max=60)])

    description = TextAreaField('Descrição do Cargo', validators=[Length(max=255)])
    
    submit = SubmitField('Registrar Novo Cargo')