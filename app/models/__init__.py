"""
Database models package
Exports all models for easy importing
"""
from app.models.base import BaseModel, TimestampMixin, User, JobListing, UserProfile

__all__ = ['BaseModel', 'TimestampMixin', 'User', 'JobListing', 'UserProfile']
