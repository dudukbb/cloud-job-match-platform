"""
Model tests
"""
import pytest
from app import db
from app.models import User, JobListing, UserProfile
from app.auth import PasswordManager


class TestUserModel:
    """User model tests"""
    
    def test_create_user(self, app):
        """Test creating a user"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password_hash=PasswordManager.hash_password('pass123'),
                first_name='Test',
                last_name='User'
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.username == 'testuser'
            assert user.is_active is True
            assert user.is_admin is False
    
    def test_user_unique_username(self, app, test_user):
        """Test username uniqueness constraint"""
        with app.app_context():
            user = User(
                username='testuser',  # Same as test_user
                email='different@example.com',
                password_hash=PasswordManager.hash_password('pass123')
            )
            db.session.add(user)
            
            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()
    
    def test_user_unique_email(self, app, test_user):
        """Test email uniqueness constraint"""
        with app.app_context():
            user = User(
                username='differentuser',
                email='test@example.com',  # Same as test_user
                password_hash=PasswordManager.hash_password('pass123')
            )
            db.session.add(user)
            
            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()
    
    def test_user_to_dict(self, app, test_user):
        """Test user to_dict method"""
        with app.app_context():
            user_dict = test_user.to_dict()
            
            assert 'id' in user_dict
            assert 'username' in user_dict
            assert 'email' in user_dict
            assert 'first_name' in user_dict
            assert 'is_active' in user_dict
            assert user_dict['username'] == 'testuser'


class TestJobListingModel:
    """JobListing model tests"""
    
    def test_create_job_listing(self, app, test_user):
        """Test creating a job listing"""
        with app.app_context():
            job = JobListing(
                title='Python Developer',
                description='Looking for a Python developer',
                company='Tech Corp',
                location='San Francisco',
                job_type='Full-time',
                experience_level='Mid',
                posted_by=test_user.id
            )
            db.session.add(job)
            db.session.commit()
            
            assert job.id is not None
            assert job.title == 'Python Developer'
            assert job.is_published is False
    
    def test_job_listing_to_dict(self, app, test_job):
        """Test job listing to_dict method"""
        with app.app_context():
            job_dict = test_job.to_dict()
            
            assert 'id' in job_dict
            assert 'title' in job_dict
            assert 'company' in job_dict
            assert 'is_published' in job_dict
            assert job_dict['title'] == 'Test Job'
    
    def test_job_listing_salary_range(self, app, test_user):
        """Test job listing with salary range"""
        with app.app_context():
            job = JobListing(
                title='Job with Salary',
                description='Job description',
                company='Company',
                salary_min=50000,
                salary_max=80000,
                posted_by=test_user.id
            )
            db.session.add(job)
            db.session.commit()
            
            assert job.salary_min == 50000
            assert job.salary_max == 80000


class TestUserProfileModel:
    """UserProfile model tests"""
    
    def test_create_user_profile(self, app, test_user):
        """Test creating a user profile"""
        with app.app_context():
            profile = UserProfile(
                user_id=test_user.id,
                bio='Software developer',
                location='San Francisco',
                experience_years=5
            )
            db.session.add(profile)
            db.session.commit()
            
            assert profile.id is not None
            assert profile.bio == 'Software developer'
    
    def test_user_profile_to_dict(self, app, test_user):
        """Test user profile to_dict method"""
        with app.app_context():
            profile = UserProfile(
                user_id=test_user.id,
                bio='Test bio'
            )
            db.session.add(profile)
            db.session.commit()
            
            profile_dict = profile.to_dict()
            
            assert 'id' in profile_dict
            assert 'user_id' in profile_dict
            assert 'bio' in profile_dict
    
    def test_user_profile_preferences(self, app, test_user):
        """Test user profile with JSON preferences"""
        with app.app_context():
            preferences = {
                'job_types': ['Full-time', 'Contract'],
                'locations': ['Remote', 'San Francisco'],
                'min_salary': 70000
            }
            
            profile = UserProfile(
                user_id=test_user.id,
                preferences=preferences
            )
            db.session.add(profile)
            db.session.commit()
            
            retrieved_profile = UserProfile.query.get(profile.id)
            assert retrieved_profile.preferences == preferences
