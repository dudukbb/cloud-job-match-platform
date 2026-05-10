"""
Utility decorators for routes and functions
"""
from functools import wraps
from flask import jsonify, request, current_app
from app import cache
import logging
import time

logger = logging.getLogger(__name__)


def require_auth(f):
    """
    Decorator to require authentication
    Add to routes that need auth
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Add authentication logic here
        # For now, just a placeholder
        return f(*args, **kwargs)
    return decorated_function


def handle_exceptions(f):
    """
    Decorator to handle exceptions in routes
    Catches common exceptions and returns appropriate error responses
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.error(f'ValueError: {str(e)}')
            return jsonify({'error': str(e)}), 400
        except PermissionError as e:
            logger.error(f'PermissionError: {str(e)}')
            return jsonify({'error': 'Access denied'}), 403
        except KeyError as e:
            logger.error(f'KeyError: {str(e)}')
            return jsonify({'error': f'Missing required field: {str(e)}'}), 400
        except Exception as e:
            logger.error(f'Unexpected error: {str(e)}', exc_info=True)
            return jsonify({'error': 'Internal server error'}), 500
    return decorated_function


def cache_response(timeout=300, key_prefix=None):
    """
    Decorator to cache route responses
    Only works for GET requests
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Optional prefix for cache key
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Only cache GET requests
            if request.method != 'GET':
                return f(*args, **kwargs)
            
            # Generate cache key
            cache_key = f"{key_prefix or f.__name__}:{request.full_path}"
            
            # Check cache
            cached_response = cache.get(cache_key)
            if cached_response:
                logger.debug(f'Cache hit: {cache_key}')
                return cached_response
            
            # Call function and cache result
            response = f(*args, **kwargs)
            cache.set(cache_key, response, timeout=timeout)
            
            return response
        return decorated_function
    return decorator


def rate_limit(limit='100/hour'):
    """
    Decorator for rate limiting
    Uses Flask-Limiter
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Rate limiting logic here
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def json_required(f):
    """
    Decorator to require JSON content type
    and parse JSON body
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        try:
            json_data = request.get_json()
            if json_data is None:
                return jsonify({'error': 'No JSON data provided'}), 400
        except Exception as e:
            return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400
        
        return f(*args, **kwargs)
    return decorated_function


def validate_request(required_fields=None, optional_fields=None):
    """
    Decorator to validate request JSON schema
    
    Args:
        required_fields: List of required field names
        optional_fields: List of optional field names
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            try:
                data = request.get_json()
            except Exception as e:
                return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400
            
            if data is None:
                data = {}
            
            # Check required fields
            if required_fields:
                for field in required_fields:
                    if field not in data or data[field] is None:
                        return jsonify({'error': f'{field} is required'}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def async_task(f):
    """
    Decorator to run function as async task
    Uses Celery if available
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            from celery import current_app as celery_app
            return celery_app.send_task(
                f'{f.__module__}.{f.__name__}',
                args=args,
                kwargs=kwargs
            )
        except Exception:
            # Fallback to sync execution
            return f(*args, **kwargs)
    return decorated_function


def log_execution(f):
    """
    Decorator to log function execution time
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f'{f.__name__} executed in {execution_time:.2f}s')
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f'{f.__name__} failed after {execution_time:.2f}s: {str(e)}')
            raise
    return decorated_function


def pagination(default_per_page=20, max_per_page=100):
    """
    Decorator to handle pagination parameters
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', default_per_page, type=int)
            
            # Validate pagination
            if page < 1:
                page = 1
            if per_page < 1:
                per_page = default_per_page
            if per_page > max_per_page:
                per_page = max_per_page
            
            return f(*args, page=page, per_page=per_page, **kwargs)
        return decorated_function
    return decorator
