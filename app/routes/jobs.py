from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Job, Application
from app.forms import JobForm
import app.extensions as ext
import json
import logging

logger = logging.getLogger(__name__)
jobs_bp = Blueprint("jobs", __name__, url_prefix="/jobs")

CACHE_KEY_PREFIX = "jobs:page:"


def _normalize_skills(skills_text: str) -> set[str]:
    return {
        skill.strip().lower()
        for skill in skills_text.split(",")
        if skill and skill.strip()
    }


def _with_match_scores(jobs_data: list[dict]) -> list[dict]:
    if not current_user.is_authenticated or current_user.is_employer:
        return jobs_data

    user_skills_raw = getattr(current_user, "skills", None)
    if not user_skills_raw:
        return jobs_data

    user_skills = _normalize_skills(user_skills_raw)
    if not user_skills:
        return jobs_data

    enriched_jobs = []
    for job in jobs_data:
        required_raw = (job.get("required_skills") or "").strip()
        if not required_raw:
            enriched_jobs.append(job)
            continue

        required_skills = _normalize_skills(required_raw)
        if not required_skills:
            enriched_jobs.append(job)
            continue

        matched = len(user_skills.intersection(required_skills))
        score = round((matched / len(required_skills)) * 100)
        enriched_jobs.append({**job, "match_score": score})

    return enriched_jobs


def _invalidate_job_cache() -> None:
    """Remove all cached job-listing pages."""
    try:
        for key in ext.redis_client.scan_iter(f"{CACHE_KEY_PREFIX}*"):
            ext.redis_client.delete(key)
    except Exception as exc:
        logger.warning("Cache invalidation failed: %s", exc)


@jobs_bp.route("/")
def list_jobs():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "").strip()
    job_type = request.args.get("type", "").strip()
    cache_key = f"{CACHE_KEY_PREFIX}{page}:{search}:{job_type}"
    ttl = current_app.config["CACHE_TTL"]

    if not search and not job_type:
        try:
            cached = ext.redis_client.get(cache_key)
            if cached:
                cached_payload = json.loads(cached)
                jobs_data = _with_match_scores(cached_payload["jobs"])
                return render_template(
                    "jobs/list.html",
                    jobs=jobs_data,
                    page=page,
                    search=search,
                    job_type=job_type,
                    from_cache=True,
                    has_next=cached_payload.get("has_next", False),
                    has_prev=cached_payload.get("has_prev", False),
                    total=cached_payload.get("total", 0),
                )
        except Exception as exc:
            logger.warning("Cache read failed: %s", exc)

    query = Job.query.filter_by(is_active=True)

    if search:
        like = f"%{search}%"
        query = query.filter(
            Job.title.ilike(like) | Job.company.ilike(like) | Job.location.ilike(like)
        )

    if job_type:
        query = query.filter_by(job_type=job_type)

    pagination = query.order_by(Job.created_at.desc()).paginate(
        page=page,
        per_page=current_app.config["JOBS_PER_PAGE"],
        error_out=False,
    )

    jobs_list = [
        {
            "id": j.id,
            "title": j.title,
            "company": j.company,
            "location": j.location,
            "job_type": j.job_type,
            "salary_range": j.salary_range,
            "required_skills": j.required_skills,
            "created_at": j.created_at.isoformat(),
        }
        for j in pagination.items
    ]

    jobs_list = _with_match_scores(jobs_list)

    if not search and not job_type:
        try:
            payload = {
                "jobs": jobs_list,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
                "total": pagination.total,
            }
            ext.redis_client.setex(cache_key, ttl, json.dumps(payload))
        except Exception as exc:
            logger.warning("Cache write failed: %s", exc)

    return render_template(
        "jobs/list.html",
        jobs=jobs_list,
        page=page,
        search=search,
        job_type=job_type,
        from_cache=False,
        has_next=pagination.has_next,
        has_prev=pagination.has_prev,
        total=pagination.total,
    )


@jobs_bp.route("/<int:job_id>")
def job_detail(job_id: int):
    job = Job.query.get_or_404(job_id)
    already_applied = False

    if current_user.is_authenticated:
        already_applied = Application.query.filter_by(
            applicant_id=current_user.id,
            job_id=job_id,
        ).first() is not None

    return render_template(
        "jobs/detail.html",
        job=job,
        already_applied=already_applied,
    )


@jobs_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_job():
    if not current_user.is_employer:
        flash("Only employers can post jobs.", "danger")
        return redirect(url_for("jobs.list_jobs"))

    form = JobForm()

    if form.validate_on_submit():
        salary_range = request.form.get("salary_range", "").strip()

        job = Job(
            title=form.title.data,
            company=form.company.data,
            location=form.location.data,
            required_skills=form.required_skills.data.strip()
            if form.required_skills.data
            else None,
            job_type=form.job_type.data,
            salary_range=salary_range or None,
            description="",
            employer_id=current_user.id,
        )

        db.session.add(job)
        db.session.commit()
        _invalidate_job_cache()

        logger.info("Job created id=%s by user=%s", job.id, current_user.id)
        flash("Job posted successfully!", "success")

        return redirect(url_for("jobs.job_detail", job_id=job.id))

    return render_template("jobs/create.html", form=form)


@jobs_bp.route("/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
def edit_job(job_id: int):
    job = Job.query.get_or_404(job_id)

    if job.employer_id != current_user.id:
        flash("You do not have permission to edit this job.", "danger")
        return redirect(url_for("jobs.job_detail", job_id=job_id))

    if request.method == "POST":
        job.title = request.form.get("title", job.title).strip()
        job.company = request.form.get("company", job.company).strip()
        job.location = request.form.get("location", job.location).strip()
        job.description = request.form.get("description", job.description).strip()
        job.salary_range = request.form.get("salary_range", "").strip()
        job.job_type = request.form.get("job_type", job.job_type)
        job.is_active = request.form.get("is_active") == "on"

        db.session.commit()
        _invalidate_job_cache()

        logger.info("Job updated id=%s by user=%s", job_id, current_user.id)
        flash("Job updated.", "success")

        return redirect(url_for("jobs.job_detail", job_id=job_id))

    return render_template("jobs/edit.html", job=job)


@jobs_bp.route("/<int:job_id>/delete", methods=["POST"])
@login_required
def delete_job(job_id: int):
    job = Job.query.get_or_404(job_id)

    if job.employer_id != current_user.id:
        flash("You do not have permission to delete this job.", "danger")
        return redirect(url_for("jobs.job_detail", job_id=job_id))

    db.session.delete(job)
    db.session.commit()
    _invalidate_job_cache()

    logger.info("Job deleted id=%s by user=%s", job_id, current_user.id)
    flash("Job deleted.", "info")

    return redirect(url_for("jobs.list_jobs"))
