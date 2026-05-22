from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Job, Application
import logging

logger = logging.getLogger(__name__)
applications_bp = Blueprint("applications", __name__, url_prefix="/applications")


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
    application = Application(
        applicant_id=current_user.id,
        job_id=job_id,
        cover_letter=cover_letter,
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


@applications_bp.route("/<int:app_id>/status", methods=["POST"])
@login_required
def update_status(app_id: int):
    application = Application.query.get_or_404(app_id)
    # Only the job's employer may update status
    if application.job.employer_id != current_user.id:
        flash("Permission denied.", "danger")
        return redirect(url_for("jobs.list_jobs"))

    new_status = request.form.get("status", "pending")
    allowed = {"pending", "reviewed", "accepted", "rejected"}
    if new_status not in allowed:
        flash("Invalid status value.", "danger")
        return redirect(url_for("jobs.job_detail", job_id=application.job_id))

    application.status = new_status
    db.session.commit()
    logger.info("Application %s status -> %s by employer %s", app_id, new_status, current_user.id)
    flash(f"Application status updated to '{new_status}'.", "success")
    return redirect(url_for("jobs.job_detail", job_id=application.job_id))
