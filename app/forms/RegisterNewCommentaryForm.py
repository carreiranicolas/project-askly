from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class RegistrarComentario(FlaskForm):
    text = TextAreaField('Adicionar interação', validators=[
        DataRequired(message="O comentário não pode estar vazio."),
        Length(min=3, max=255, message="O texto deve ter entre 3 e 255 caracteres.")
    ])
    submit = SubmitField('Enviar Mensagem')