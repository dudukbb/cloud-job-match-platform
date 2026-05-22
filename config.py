import os
from datetime import timedelta


class Config:
    # Security
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")

    # Database — Factor III: store config in env
    _database_url = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/jobmatch"
    )
    # Heroku-style URLs may use postgres://, normalize for SQLAlchemy.
    if _database_url.startswith("postgres://"):
        _database_url = _database_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Redis
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TTL = int(os.environ.get("CACHE_TTL", 300))  # seconds

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.environ.get("SESSION_LIFETIME", 3600))
    )

    # Logging — Factor XI: logs as event streams
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    # Pagination
    JOBS_PER_PAGE = int(os.environ.get("JOBS_PER_PAGE", 10))


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", "sqlite:///:memory:"
    )
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False

    # Keep compatibility with current setup while allowing strict production hardening.
    REQUIRE_STRONG_SECRET = os.environ.get("REQUIRE_STRONG_SECRET", "false").lower() == "true"


config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
