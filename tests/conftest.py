"""
Pytest configuration and fixtures
"""
import pytest
import os
from app import create_app, db
from app.models import User, JobListing, UserProfile
from app.auth import PasswordManager


@pytest.fixture
def app():
    """
    Create and configure a test app
    """
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """
    A test client for the app
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    A test runner for the app's CLI commands
    """
    return app.test_cli_runner()


@pytest.fixture
def app_context(app):
    """
    Application context for tests
    """
    with app.app_context():
        yield app


@pytest.fixture
def test_user(app):
    """
    Create a test user
    """
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=PasswordManager.hash_password('testpass123'),
            first_name='Test',
            last_name='User'
        )
        db.session.add(user)
        db.session.commit()
        
        # Create default profile
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()
        
        yield user


@pytest.fixture
def test_admin_user(app):
    """
    Create a test admin user
    """
    with app.app_context():
        user = User(
            username='adminuser',
            email='admin@example.com',
            password_hash=PasswordManager.hash_password('adminpass123'),
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        db.session.add(user)
        db.session.commit()
        
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()
        
        yield user


@pytest.fixture
def test_job(app, test_user):
    """
    Create a test job listing
    """
    with app.app_context():
        job = JobListing(
            title='Test Job',
            description='A test job description',
            company='Test Company',
            location='Test City',
            job_type='Full-time',
            experience_level='Mid',
            is_published=True,
            posted_by=test_user.id
        )
        db.session.add(job)
        db.session.commit()
        
        yield job


@pytest.fixture
def auth_token(app, test_user):
    """
    Generate an auth token for test user
    """
    from app.auth import TokenManager
    
    with app.app_context():
        token = TokenManager.generate_access_token(test_user.id)
        yield token


@pytest.fixture
def auth_headers(auth_token):
    """
    Headers with authentication token
    """
    return {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def admin_auth_token(app, test_admin_user):
    """
    Generate an auth token for admin user
    """
    from app.auth import TokenManager
    
    with app.app_context():
        token = TokenManager.generate_access_token(test_admin_user.id)
        yield token


@pytest.fixture
def admin_auth_headers(admin_auth_token):
    """
    Headers with admin authentication token
    """
    return {
        'Authorization': f'Bearer {admin_auth_token}',
        'Content-Type': 'application/json'
    }
