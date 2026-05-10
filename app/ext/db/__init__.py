from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)

def register_models():
    import app.models.user
    import app.models.category
    import app.models.ticket
    import app.models.commentary
    import app.models.history