from pathlib import Path
from uuid import uuid4
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import Job, Application
from app.skill_matching import (
    extract_resume_text,
    extract_skills_from_text,
    format_skills,
    normalize_skills,
    build_match_summary,
)
import logging

logger = logging.getLogger(__name__)
applications_bp = Blueprint("applications", __name__, url_prefix="/applications")
ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx"}
STATUS_LOOKUP = {
    "pending": "Pending",
    "under review": "Under Review",
    "under_review": "Under Review",
    "under-review": "Under Review",
    "reviewed": "Under Review",
    "accepted": "Accepted",
    "rejected": "Rejected",
}


def _canonical_status(raw_status: str | None) -> str | None:
    if not raw_status:
        return None
    return STATUS_LOOKUP.get(raw_status.strip().lower())


def _resume_upload_dir() -> Path:
    upload_dir = Path(current_app.root_path).parent / "uploads" / "resumes"
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


@applications_bp.route("/apply/<int:job_id>", methods=["POST"])
@login_required
def apply(job_id: int):
    if current_user.is_employer:
        flash("Employers cannot apply for jobs.", "warning")
        return redirect(url_for("jobs.job_detail", job_id=job_id))

    job = Job.query.get_or_404(job_id)
    if not job.is_active:
        flash("This job is no longer accepting applications.", "warning")
        return redirect(url_for("jobs.job_detail", job_id=job_id))

    existing = Application.query.filter_by(
        applicant_id=current_user.id, job_id=job_id
    ).first()
    if existing:
        flash("You have already applied for this job.", "info")
        return redirect(url_for("jobs.job_detail", job_id=job_id))

    cover_letter = request.form.get("cover_letter", "").strip()
    resume_filename = None
    resume_path = None

    resume = request.files.get("resume")
    if resume and resume.filename:
        try:
            safe_original_name = secure_filename(resume.filename)
            extension = Path(safe_original_name).suffix.lower()
            resume_bytes = resume.read()

            if extension in ALLOWED_RESUME_EXTENSIONS and resume_bytes:
                stored_name = f"{uuid4().hex}{extension}"
                destination = _resume_upload_dir() / stored_name
                destination.write_bytes(resume_bytes)

                resume_filename = safe_original_name
                resume_path = str(destination)

            extracted_text = extract_resume_text(safe_original_name, resume_bytes)
            extracted_skills = extract_skills_from_text(extracted_text)
            if extracted_skills:
                existing_skills = normalize_skills(current_user.skills or "")
                combined_skills = existing_skills.union(extracted_skills)
                current_user.skills = format_skills(combined_skills)
                flash("Resume processed. Skills profile updated for better job matching.", "info")
            else:
                flash("Resume uploaded, but no known technical skills were extracted.", "warning")
        except Exception:
            flash("Resume upload could not be processed. Application was still submitted.", "warning")

    application = Application(
        applicant_id=current_user.id,
        job_id=job_id,
        cover_letter=cover_letter,
        resume_filename=resume_filename,
        resume_path=resume_path,
    )
    db.session.add(application)
    db.session.commit()
    logger.info("Application submitted user=%s job=%s", current_user.id, job_id)
    flash("Application submitted successfully!", "success")
    return redirect(url_for("applications.my_applications"))


@applications_bp.route("/mine")
@login_required
def my_applications():
    apps = (
        Application.query
        .filter_by(applicant_id=current_user.id)
        .order_by(Application.created_at.desc())
        .all()
    )
    return render_template("applications/my_applications.html", applications=apps)


@applications_bp.route("/review")
@login_required
def review_applications():
    if not current_user.is_employer:
        flash("Only employers can access application reviews.", "warning")
        return redirect(url_for("jobs.list_jobs"))

    apps = (
        Application.query
        .join(Job, Application.job_id == Job.id)
        .filter(Job.employer_id == current_user.id)
        .order_by(Application.created_at.desc())
        .all()
    )

    applications_with_match = []
    for application in apps:
        match_summary = build_match_summary(
            application.applicant.skills or "",
            application.job.required_skills or "",
        )
        applications_with_match.append({
            "application": application,
            "match": match_summary,
        })

    return render_template(
        "applications/review.html",
        applications_with_match=applications_with_match,
    )


@applications_bp.route("/<int:app_id>/resume")
@login_required
def download_resume(app_id: int):
    application = Application.query.get_or_404(app_id)

    is_owner_employer = current_user.is_employer and application.job.employer_id == current_user.id
    is_applicant = application.applicant_id == current_user.id
    if not (is_owner_employer or is_applicant):
        flash("You do not have permission to access this resume.", "danger")
        return redirect(url_for("jobs.list_jobs"))

    if not application.resume_path:
        flash("No resume uploaded for this application.", "warning")
        return redirect(request.referrer or url_for("jobs.list_jobs"))

    path = Path(application.resume_path)
    if not path.exists() or not path.is_file():
        flash("Resume file is not available.", "warning")
        return redirect(request.referrer or url_for("jobs.list_jobs"))

    download_name = application.resume_filename or path.name
    return send_file(path, as_attachment=False, download_name=download_name)


@applications_bp.route("/<int:app_id>/status", methods=["POST"])
@login_required
def update_status(app_id: int):
    requested_status = request.form.get("status", "")
    return _update_application_status(app_id, requested_status)


def _update_application_status(app_id: int, requested_status: str):
    application = Application.query.get_or_404(app_id)
    if application.job.employer_id != current_user.id:
        flash("Permission denied.", "danger")
        return redirect(url_for("jobs.list_jobs"))

    canonical_status = _canonical_status(requested_status)
    if not canonical_status:
        flash("Invalid status value.", "danger")
        return redirect(request.referrer or url_for("applications.review_applications"))

    application.status = canonical_status
    db.session.commit()
    logger.info("Application %s status -> %s by employer %s", app_id, canonical_status, current_user.id)
    flash(f"Application status updated to '{canonical_status}'.", "success")
    return redirect(request.referrer or url_for("applications.review_applications"))


@applications_bp.route("/<int:app_id>/status/<string:new_status>", methods=["POST"])
@login_required
def update_status_by_path(app_id: int, new_status: str):
    return _update_application_status(app_id, new_status)
