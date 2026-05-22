import logging
import sys
import os
from flask import Flask
from sqlalchemy import inspect, text
from werkzeug.middleware.proxy_fix import ProxyFix
from config import config_map
from app.extensions import db, login_manager, bcrypt, csrf
import redis as redis_lib


logger = logging.getLogger(__name__)


def configure_logging(log_level: str) -> None:
    """Factor XI — emit structured logs to stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(getattr(logging, log_level.upper(), logging.INFO))


def ensure_local_schema_compatibility() -> None:
    """Apply safe additive schema updates for local/dev environments."""
    inspector = inspect(db.engine)
    tables = set(inspector.get_table_names())
    if "jobs" not in tables:
        return

    columns = {col["name"] for col in inspector.get_columns("jobs")}

    with db.engine.begin() as conn:
        if "required_skills" not in columns:
            conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS required_skills TEXT"))
            logger.info("Applied schema patch: jobs.required_skills")

        if "job_type" not in columns:
            conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS job_type VARCHAR(50)"))
            logger.info("Applied schema patch: jobs.job_type")

        if "employment_type" in columns:
            conn.execute(text(
                """
                UPDATE jobs
                SET job_type = employment_type
                WHERE employment_type IS NOT NULL
                  AND (job_type IS NULL OR job_type = '')
                """
            ))
            logger.info("Applied schema patch: backfilled jobs.job_type from jobs.employment_type")


def create_app(config_name: str = "default") -> Flask:
    app = Flask(__name__)
    cfg = config_map.get(config_name, config_map["default"])
    app.config.from_object(cfg)

    configure_logging(app.config["LOG_LEVEL"])

    # Factor III hardening in production, opt-in for backwards compatibility.
    require_strong_secret = bool(app.config.get("REQUIRE_STRONG_SECRET", False))
    if require_strong_secret and app.config.get("SECRET_KEY") == "change-me-in-production":
        raise RuntimeError("SECRET_KEY must be set to a strong value in production")

    if os.environ.get("TRUST_PROXY", "false").lower() == "true":
        # Respect X-Forwarded-* headers when running behind cloud load balancers.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    # Initialise extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # Redis — Factor IV: backing services as attached resources
    import app.extensions as ext
    ext.redis_client = redis_lib.from_url(
        app.config["REDIS_URL"], decode_responses=True
    )

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.jobs import jobs_bp
    from app.routes.applications import applications_bp
    from app.routes.health import health_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(health_bp)

    # Create tables (idempotent)
    auto_create_tables = os.environ.get("AUTO_CREATE_TABLES", "true").lower() == "true"
    with app.app_context():
        if auto_create_tables:
            db.create_all()
            ensure_local_schema_compatibility()
        else:
            logger.info("AUTO_CREATE_TABLES=false, skipping startup schema creation")

    return app
