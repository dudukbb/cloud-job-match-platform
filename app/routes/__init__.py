"""
Routes package - Blueprint definitions and registration
"""
from flask import Blueprint

# Health check blueprint
health_bp = Blueprint('health', __name__)

# API blueprint
api_bp = Blueprint('api', __name__)

# Authentication blueprint
auth_bp = Blueprint('auth', __name__)

__all__ = ['health_bp', 'api_bp', 'auth_bp']