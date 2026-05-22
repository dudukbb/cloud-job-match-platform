from flask import Blueprint, jsonify
from app.extensions import db
import app.extensions as ext
import logging

logger = logging.getLogger(__name__)
health_bp = Blueprint("health", __name__)


@health_bp.route("/health")
def health():
    """Factor IX — disposability; liveness probe for orchestrators."""
    status = {"status": "ok", "checks": {}}
    http_status = 200

    # Database check
    try:
        db.session.execute(db.text("SELECT 1"))
        status["checks"]["database"] = "ok"
    except Exception as exc:
        logger.error("Health check — DB error: %s", exc)
        status["checks"]["database"] = "error"
        status["status"] = "degraded"
        http_status = 503

    # Redis check
    try:
        if ext.redis_client is None:
            raise RuntimeError("Redis client not initialized")
        ext.redis_client.ping()
        status["checks"]["redis"] = "ok"
    except Exception as exc:
        logger.error("Health check — Redis error: %s", exc)
        status["checks"]["redis"] = "error"
        status["status"] = "degraded"
        http_status = 503

    return jsonify(status), http_status


@health_bp.route("/")
def index():
    from flask import redirect, url_for
    return redirect(url_for("jobs.list_jobs"))
