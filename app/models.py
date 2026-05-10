from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20), default='solicitante')  
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.now)

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(255))
    ativo = db.Column(db.Boolean, default=True)

class Chamado(db.Model):
    __tablename__ = 'chamados'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    prioridade = db.Column(db.String(20), default='media')
    status = db.Column(db.String(30), default='Aberto')
    solicitante_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    atendente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.now)
    atualizado_em = db.Column(db.DateTime, onupdate=datetime.now)

    solicitante = db.relationship("Usuario", foreign_keys=[solicitante_id])
    atendente = db.relationship("Usuario", foreign_keys=[atendente_id])

class Comentario(db.Model):
    __tablename__ = 'comentarios'
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.now)
    # Falta id_chamado
    #Falta id_autor

class HistoricoStatus(db.Model):
    __tablename__ = 'historico_status'

    id = db.Column(db.Integer, primary_key=True)
    chamado_id = db.Column(db.Integer, db.ForeignKey('chamados.id')) 
    status_anterior = db.Column(db.String(30)) 
    status_novo = db.Column(db.String(30)) 
    alterado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id')) 
    criado_em = db.Column(db.DateTime, default=datetime.now) 
    # Falta relacionamento explicito de: chamado
    # Falta relacionamento explicito de: alterado por