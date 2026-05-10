"""
Flask Application Factory
12-Factor App Architecture
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


def create_app(config_name=None):
    """
    Application Factory Function
    Creates and configures the Flask application
    
    Args:
        config_name: Configuration environment (development, testing, production, staging)
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    from app.config import config
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    
    # Initialize CORS
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # Initialize rate limiting if enabled
    if app.config['RATELIMIT_ENABLED']:
        limiter.init_app(app)
    
    # Create instance folder if not exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Setup logging
    setup_logging(app)
    
    # Register database context
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # App initialization logging
    app.logger.info(
        f"App initialized - Environment: {app.config['ENVIRONMENT']}, "
        f"Version: {app.config['APP_VERSION']}"
    )
    
    return app


def setup_logging(app):
    """Configure application logging"""
    if app.debug:
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)
    
    # Only add file handler in production
    if not app.debug and not app.config['TESTING']:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [%(name)s:%(funcName)s:%(lineno)d]'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Also log to error file
        error_file_handler = RotatingFileHandler(
            'logs/error.log',
            maxBytes=10240000,
            backupCount=10
        )
        error_file_handler.setFormatter(file_formatter)
        error_file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(error_file_handler)
        
        app.logger.info('Flask application startup')


def register_blueprints(app):
    """Register application blueprints"""
    from app.routes.health import health_bp
    from app.routes.api import api_bp
    from app.routes.auth import auth_bp
    
    app.register_blueprint(health_bp, url_prefix='/health')
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/auth')


def register_error_handlers(app):
    """Register error handlers for common HTTP errors"""
    from flask import jsonify
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Bad Request"""
        return jsonify({
            'error': 'Bad Request',
            'message': str(error.description)
        }), 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        """Unauthorized"""
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Forbidden"""
        return jsonify({
            'error': 'Forbidden',
            'message': 'Access denied'
        }), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Not Found"""
        return jsonify({
            'error': 'Not Found',
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Internal Server Error"""
        db.session.rollback()
        app.logger.error(f'Internal server error: {str(error)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(503)
    def service_unavailable_error(error):
        """Service Unavailable"""
        return jsonify({
            'error': 'Service Unavailable',
            'message': 'Service is temporarily unavailable'
        }), 503


def register_cli_commands(app):
    """Register CLI commands"""
    import click
    
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        db.create_all()
        click.echo('Initialized the database.')
    
    @app.cli.command()
    def drop_db():
        """Drop all database tables."""
        if click.confirm('Are you sure you want to drop all tables?'):
            db.drop_all()
            click.echo('Dropped all tables.')
    
    @app.cli.command()
    def seed_db():
        """Seed the database with sample data."""
        click.echo('Database seeding not yet implemented.')
