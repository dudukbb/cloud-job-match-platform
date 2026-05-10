"""
User service
Business logic for users and profiles
"""
from app import db
from app.models import UserProfile


def update_profile(user_id, data):
    profile = UserProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)

    allowed_fields = [
        "full_name",
        "bio",
        "location",
        "phone",
        "linkedin_url",
        "github_url",
        "skills",
        "experience_years",
        "education",
    ]

    for field in allowed_fields:
        if field in data:
            setattr(profile, field, data[field])

    db.session.commit()
    return profile