from flask_wtf import CSRFProtect

csrf = CSRFProtect()

def init_app(app):
    if not app.config.get("TESTING"):
        csrf.init_app(app)