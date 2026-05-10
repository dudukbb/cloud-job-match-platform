"""
Authentication routes
User registration, login, token management
"""
from app.routes import auth_bp
from flask import request, jsonify, current_app, g
from app import db
from app.models import User
from app.auth import TokenManager, PasswordManager, require_auth, token_required
from app.services import user_service
import logging

logger = logging.getLogger(__name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Request JSON:
        - username: string (required)
        - email: string (required)
        - password: string (required)
        - first_name: string (optional)
        - last_name: string (optional)
    """
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    # Create new user
    try:
        user = user_service.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        
        logger.info(f'New user registered: {user.username}')
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
    except Exception as e:
        logger.error(f'Registration error: {str(e)}')
        return jsonify({'error': 'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user and return JWT tokens
    
    Request JSON:
        - username or email: string (required)
        - password: string (required)
    
    Response:
        - access_token: JWT access token
        - refresh_token: JWT refresh token
        - user: User object
    """
    data = request.get_json()
    
    if not data or not data.get('password'):
        return jsonify({'error': 'Username/email and password required'}), 400
    
    # Find user by username or email
    user = User.query.filter(
        (User.username == data.get('username')) | 
        (User.email == data.get('email'))
    ).first()
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Verify password
    if not PasswordManager.verify_password(data['password'], user.password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is inactive'}), 403
    
    # Generate tokens
    access_token = TokenManager.generate_access_token(user.id)
    refresh_token = TokenManager.generate_refresh_token(user.id)
    
    # Update last login
    user.last_login = db.func.now()
    db.session.commit()
    
    logger.info(f'User logged in: {user.username}')
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """
    Refresh access token using refresh token
    
    Request JSON:
        - refresh_token: JWT refresh token (required)
    
    Response:
        - access_token: New JWT access token
    """
    data = request.get_json()
    
    if not data or not data.get('refresh_token'):
        return jsonify({'error': 'Refresh token required'}), 400
    
    payload = TokenManager.verify_token(data['refresh_token'], token_type='refresh')
    if not payload:
        return jsonify({'error': 'Invalid or expired refresh token'}), 401
    
    # Generate new access token
    access_token = TokenManager.generate_access_token(payload['user_id'])
    
    return jsonify({
        'access_token': access_token
    }), 200


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """
    Get current authenticated user
    Requires: Authorization header with access token
    """
    user = User.query.get(g.user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200


@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """
    Logout user (client-side token removal)
    In production, implement token blacklisting
    """
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """
    Change user password
    Requires: Authorization header with access token
    
    Request JSON:
        - current_password: string (required)
        - new_password: string (required)
    """
    data = request.get_json()
    
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current and new password required'}), 400
    
    user = User.query.get(g.user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Verify current password
    if not PasswordManager.verify_password(data['current_password'], user.password_hash):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Update password
    user.password_hash = PasswordManager.hash_password(data['new_password'])
    db.session.commit()
    
    logger.info(f'User changed password: {user.username}')
    
    return jsonify({'message': 'Password changed successfully'}), 200


@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get user profile"""
    from app.models import UserProfile
    
    user = User.query.get(g.user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    profile = UserProfile.query.filter_by(user_id=g.user_id).first()
    
    return jsonify({
        'user': user.to_dict(),
        'profile': profile.to_dict() if profile else None
    }), 200


@auth_bp.route('/verify-token', methods=['GET'])
def verify_token_endpoint():
    """Verify if token is valid"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return jsonify({'valid': False}), 200
    
    try:
        token = auth_header.split(' ')[1]
    except IndexError:
        return jsonify({'valid': False}), 200
    
    payload = TokenManager.verify_token(token)
    
    return jsonify({
        'valid': payload is not None,
        'user_id': payload['user_id'] if payload else None
    }), 200
