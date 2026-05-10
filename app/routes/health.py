from flask import Blueprint, jsonify
from datetime import datetime

health_bp = Blueprint("health", __name__)


@health_bp.route("/", methods=["GET"])
def health_check():
    status = {
        "status": "healthy",
        "service": "Job Match",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

    return jsonify(status), 200