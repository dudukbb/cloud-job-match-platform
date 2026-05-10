"""
Authentication utilities
JWT and password hashing support
"""
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify
from bcrypt import hashpw, checkpw, gensalt
import logging

logger = logging.getLogger(__name__)


class TokenManager:
    """Manage JWT tokens"""
    
    @staticmethod
    def generate_access_token(user_id, expires_in=None):
        """
        Generate JWT access token
        
        Args:
            user_id: User ID (string or UUID)
            expires_in: Token expiration in seconds
        
        Returns:
            JWT token string
        """
        if expires_in is None:
            expires_in = current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        
        payload = {
            'user_id': str(user_id),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        token = jwt.encode(
            payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        return token
    
    @staticmethod
    def generate_refresh_token(user_id):
        """
        Generate JWT refresh token
        
        Args:
            user_id: User ID (string or UUID)
        
        Returns:
            JWT token string
        """
        expires_in = current_app.config['JWT_REFRESH_TOKEN_EXPIRES']
        
        payload = {
            'user_id': str(user_id),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        token = jwt.encode(
            payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        return token
    
    @staticmethod
    def verify_token(token, token_type='access'):
        """
        Verify JWT token
        
        Args:
            token: JWT token string
            token_type: Type of token ('access' or 'refresh')
        
        Returns:
            Payload dict if valid, None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            
            if payload.get('type') != token_type:
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning(f'Token expired: {token_type}')
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f'Invalid token: {str(e)}')
            return None
        except Exception as e:
            logger.error(f'Token verification error: {str(e)}')
            return None


class PasswordManager:
    """Manage password hashing and verification"""
    
    @staticmethod
    def hash_password(password):
        """
        Hash password using bcrypt
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password
        """
        if not isinstance(password, bytes):
            password = password.encode('utf-8')
        
        salt = gensalt(rounds=12)
        return hashpw(password, salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password, password_hash):
        """
        Verify password against hash
        
        Args:
            password: Plain text password
            password_hash: Hashed password
        
        Returns:
            True if password matches, False otherwise
        """
        if not isinstance(password, bytes):
            password = password.encode('utf-8')
        
        if not isinstance(password_hash, bytes):
            password_hash = password_hash.encode('utf-8')
        
        return checkpw(password, password_hash)


def require_auth(f):
    """
    Decorator to require JWT authentication
    Verifies Authorization header and sets g.user_id
    
    Usage:
        @app.route('/protected')
        @require_auth
        def protected():
            return {'user_id': g.user_id}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import g
        
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid authorization header'}), 401
        
        if not token:
            return jsonify({'error': 'Authorization token required'}), 401
        
        payload = TokenManager.verify_token(token, token_type='access')
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        g.user_id = payload['user_id']
        return f(*args, **kwargs)
    
    return decorated_function


def require_admin(f):
    """
    Decorator to require admin authentication
    Must have require_auth decorator first
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import g
        from app.models import User
        
        # This assumes require_auth has already been applied
        if not hasattr(g, 'user_id'):
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user is admin
        user = User.query.get(g.user_id)
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def token_required(f):
    """
    Alternative decorator using parameter
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import g
        
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization token required'}), 401
        
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'error': 'Invalid authorization header'}), 401
        
        payload = TokenManager.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        g.user_id = payload['user_id']
        g.token_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated_function