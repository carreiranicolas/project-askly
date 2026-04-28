"""Application configuration settings."""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_EXP_SECONDS = int(os.environ.get('JWT_EXP_SECONDS') or 3600)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    ITEMS_PER_PAGE = 10
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    STATUS_COLORS = {
        'ABERTO': '#209cee',
        'EM_ATENDIMENTO': '#3273dc',
        'AGUARDANDO_RETORNO': '#00d1b2',
        'RESOLVIDO': '#ffdd57',
        'FECHADO': '#ff3860',
    }
    
    STATUS_ENUM = ['ABERTO', 'EM_ATENDIMENTO', 'AGUARDANDO_RETORNO', 'RESOLVIDO', 'FECHADO']
    PRIORIDADE_ENUM = ['BAIXA', 'MEDIA', 'ALTA', 'CRITICA']
    PERFIL_ENUM = ['solicitante', 'atendente', 'admin']
    
    SWAGGER_UI_DOC_EXPANSION = 'list'
    RESTX_MASK_SWAGGER = False


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://askly:askly_dev_password@localhost:5432/askly_db'
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    # Prefer TEST_DATABASE_URL (documented). Keep fallback for older name TEST_DATABASE_URL.
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("TEST_DATABASE_URL")
        or os.environ.get("TEST_DATABASE_URL")
        or "postgresql://askly:askly_dev_password@localhost:5432/askly_test_db"
    )
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SESSION_COOKIE_SECURE = True
    
    TALISMAN_FORCE_HTTPS = True
    TALISMAN_STRICT_TRANSPORT_SECURITY = True
    TALISMAN_CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'style-src': ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
        'script-src': ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
        'font-src': ["'self'", "https://cdn.jsdelivr.net"],
    }


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}


def get_config(env: str | None = None) -> type[Config]:
    """Get configuration class based on environment."""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, DevelopmentConfig)
