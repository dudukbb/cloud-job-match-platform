"""
Application Configuration - 12-Factor App Compliance
All configuration from environment variables
"""
import os
from datetime import timedelta


class Config:
    """Base configuration - 12-Factor compliant"""
    
    # ========== Flask Core ==========
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    PROPAGATE_EXCEPTIONS = True
    
    # ========== Database (PostgreSQL) ==========
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', 10)),
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', 3600)),
        'pool_pre_ping': True,
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 20)),
    }
    
    # PostgreSQL Connection
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'job_match')
    
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    
    # ========== Redis & Caching ==========
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 300))
    
    # ========== Session Configuration ==========
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'job_match_session'
    
    # ========== JWT Authentication ==========
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))  # 30 days
    
    # ========== Security ==========
    SESSION_REFRESH_EACH_REQUEST = True
    
    # ========== CORS ==========
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    
    # ========== Rate Limiting ==========
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_STORAGE_URL = REDIS_URL
    
    # ========== Logging ==========
    LOG_TO_STDOUT = os.getenv('LOG_TO_STDOUT', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # ========== API ==========
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    API_VERSION = '1.0'
    
    # ========== Application ==========
    APP_NAME = 'Job Match'
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    ENVIRONMENT = os.getenv('FLASK_ENV', 'development')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_RECORD_QUERIES = True
    RATELIMIT_ENABLED = False
    TEMPLATES_AUTO_RELOAD = True
    LOG_LEVEL = 'DEBUG'
    
    DB_NAME = os.getenv('DB_NAME', 'job_match_dev')
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@"
        f"{Config.DB_HOST}:{Config.DB_PORT}/{DB_NAME}"
    )


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    REDIS_URL = 'redis://localhost:6379/15'
    CACHE_REDIS_URL = REDIS_URL
    RATELIMIT_ENABLED = False
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'
    LOG_TO_STDOUT = True
    LOG_LEVEL = 'WARNING'
    
    # Production security
    SESSION_COOKIE_NAME = '__secure_session'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)


class StagingConfig(ProductionConfig):
    """Staging configuration"""
    LOG_LEVEL = 'INFO'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}
