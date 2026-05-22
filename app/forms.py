from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

EMPLOYMENT_TYPES = [
    ("Full-time", "Full-time"),
    ("Part-time", "Part-time"),
    ("Contract", "Contract"),
    ("Remote", "Remote"),
    ("Internship", "Internship"),
]


class JobForm(FlaskForm):
    title = StringField(
        "Job Title",
        validators=[DataRequired(message="Job title is required."), Length(max=200)],
        render_kw={"placeholder": "e.g. Senior Python Developer"},
    )
    company = StringField(
        "Company",
        validators=[DataRequired(message="Company name is required."), Length(max=200)],
        render_kw={"placeholder": "Your company name"},
    )
    location = StringField(
        "Location",
        validators=[DataRequired(message="Location is required."), Length(max=200)],
        render_kw={"placeholder": "e.g. New York, NY or Remote"},
    )
    required_skills = TextAreaField(
        "Required Skills",
        validators=[Optional(), Length(max=1000)],
        render_kw={
            "placeholder": "e.g. Python, SQL, Docker (comma-separated)",
            "rows": "4",
        },
    )
    job_type = SelectField(
        "Employment Type",
        choices=EMPLOYMENT_TYPES,
        validators=[DataRequired()],
    )
