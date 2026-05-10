"""
User Service
Business logic for user operations
"""
from app import db
from app.models import User, UserProfile
from app.auth import PasswordManager
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def create_user(username, email, password, first_name=None, last_name=None):
    """
    Create a new user
    
    Args:
        username: User's username
        email: User's email
        password: Plain text password (will be hashed)
        first_name: User's first name (optional)
        last_name: User's last name (optional)
    
    Returns:
        Created User object
    """
    user = User(
        username=username,
        email=email,
        password_hash=PasswordManager.hash_password(password),
        first_name=first_name,
        last_name=last_name,
        is_active=True
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Create default profile
    profile = UserProfile(user_id=user.id)
    db.session.add(profile)
    db.session.commit()
    
    logger.info(f'User created: {user.username}')
    return user


def get_user_by_username(username):
    """Get user by username"""
    return User.query.filter_by(username=username).first()


def get_user_by_email(email):
    """Get user by email"""
    return User.query.filter_by(email=email).first()


def update_profile(user_id, data):
    """
    Update user profile
    
    Args:
        user_id: User ID
        data: Profile data dictionary
    
    Returns:
        Updated UserProfile object
    """
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)
    
    # Update fields
    for key, value in data.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
    
    profile.updated_at = datetime.utcnow()
    db.session.commit()
    
    logger.info(f'User profile updated: {user_id}')
    return profile


def deactivate_user(user_id):
    """Deactivate a user account"""
    user = User.query.get(user_id)
    if user:
        user.is_active = False
        db.session.commit()
        logger.info(f'User deactivated: {user_id}')
    return user


def activate_user(user_id):
    """Activate a user account"""
    user = User.query.get(user_id)
    if user:
        user.is_active = True
        db.session.commit()
        logger.info(f'User activated: {user_id}')
    return user
