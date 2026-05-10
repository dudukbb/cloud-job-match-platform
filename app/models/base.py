"""
Base model classes for all database models
Provides common functionality for all models
"""
from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid


class BaseModel(db.Model):
    """
    Abstract base model with common attributes
    All models should inherit from this
    """
    __abstract__ = True
    
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        index=True
    )


class User(BaseModel, TimestampMixin):
    """User model"""
    __tablename__ = 'users'
    
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class JobListing(BaseModel, TimestampMixin):
    """Job Listing model"""
    __tablename__ = 'job_listings'
    
    title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    company = db.Column(db.String(255), nullable=False, index=True)
    location = db.Column(db.String(255))
    salary_min = db.Column(db.Float)
    salary_max = db.Column(db.Float)
    job_type = db.Column(db.String(50))  # Full-time, Part-time, Contract, etc.
    experience_level = db.Column(db.String(50))  # Entry, Mid, Senior, etc.
    skills_required = db.Column(db.Text)  # JSON or comma-separated
    is_published = db.Column(db.Boolean, default=False, nullable=False)
    posted_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<JobListing {self.title}>'
    
    def to_dict(self):
        """Convert job listing to dictionary"""
        return {
            'id': str(self.id),
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'job_type': self.job_type,
            'experience_level': self.experience_level,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class UserProfile(BaseModel, TimestampMixin):
    """User Profile model"""
    __tablename__ = 'user_profiles'
    
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), unique=True, nullable=False)
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(500))
    location = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(500))
    skills = db.Column(db.Text)  # JSON or comma-separated
    experience_years = db.Column(db.Integer)
    preferences = db.Column(db.JSON)  # Job preferences
    
    def __repr__(self):
        return f'<UserProfile {self.user_id}>'
    
    def to_dict(self):
        """Convert profile to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'bio': self.bio,
            'location': self.location,
            'skills': self.skills,
            'experience_years': self.experience_years,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
