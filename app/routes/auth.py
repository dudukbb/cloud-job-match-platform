from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
VALID_ROLES = {"employer", "job_seeker"}


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("jobs.list_jobs"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        role = request.form.get("role", "job_seeker").strip().lower()
        skills = request.form.get("skills", "").strip()

        if role not in VALID_ROLES:
            flash("Invalid role selected.", "danger")
            return render_template("auth/register.html", selected_role="job_seeker")

        is_employer = role == "employer"

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("auth/register.html", selected_role=role)

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("auth/register.html", selected_role=role)

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return render_template("auth/register.html", selected_role=role)

        if User.query.filter(
            (User.username == username) | (User.email == email)
        ).first():
            flash("Username or email already taken.", "danger")
            return render_template("auth/register.html", selected_role=role)

        user = User(
            username=username,
            email=email,
            is_employer=is_employer,
            skills=skills if (not is_employer and skills) else None,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        logger.info("New user registered: %s", username)
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", selected_role="job_seeker")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("jobs.list_jobs"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            logger.info("User logged in: %s", user.username)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("jobs.list_jobs"))

        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logger.info("User logged out: %s", current_user.username)
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
