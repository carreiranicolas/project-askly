import sys
from src.presentation.app_factory import create_app
from src.infrastructure.persistence.sqlalchemy.models import db, CategoriaModel

app = create_app('development')
with app.app_context():
    areas_desejadas = ['RH', 'INFRA', 'FINANCEIRO', 'COMERCIAL', 'DESENVOLVIMENTO']
    # Delete old that are not in areas_desejadas
    for cat in CategoriaModel.query.all():
        if cat.nome not in areas_desejadas:
            db.session.delete(cat)
    
    # Create missing
    existentes = [c.nome for c in CategoriaModel.query.all()]
    for nome in areas_desejadas:
        if nome not in existentes:
            db.session.add(CategoriaModel(nome=nome, ativa=True))
    
    db.session.commit()
    print("Áreas atualizadas com sucesso!")
