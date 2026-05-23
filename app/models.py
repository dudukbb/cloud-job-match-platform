from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, login_manager, bcrypt


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_employer = db.Column(db.Boolean, default=False)
    skills = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    job_postings = db.relationship("Job", backref="employer", lazy="dynamic", cascade="all, delete-orphan")
    applications = db.relationship("Application", backref="applicant", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text)
    salary_range = db.Column(db.String(100))
    job_type = db.Column(db.String(50), default="Full-time")  # Full-time, Part-time, Contract, Remote, Internship
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    applications = db.relationship("Application", backref="job", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Job {self.title} @ {self.company}>"


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    cover_letter = db.Column(db.Text)
    resume_filename = db.Column(db.String(255))
    resume_path = db.Column(db.String(500))
    status = db.Column(db.String(30), default="pending")  # pending, reviewed, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applicant_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("applicant_id", "job_id", name="uq_applicant_job"),
    )

    def __repr__(self) -> str:
        return f"<Application user={self.applicant_id} job={self.job_id}>"
