"""
REST API routes
Core API endpoints for the application
"""
from flask import jsonify, request, g, current_app
from app.routes import api_bp
from app import db, cache
from app.models import JobListing, User
from app.auth import token_required
import app.services.job_service as job_service
import app.services.user_service as user_service
import logging

logger = logging.getLogger(__name__)


@api_bp.route('/status', methods=['GET'])
def api_status():
    """API status endpoint"""
    return jsonify({
        'api': 'online',
        'version': current_app.config['API_VERSION'],
        'environment': current_app.config['ENVIRONMENT']
    }), 200


@api_bp.route('/info', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': current_app.config['APP_NAME'],
        'version': current_app.config['APP_VERSION'],
        'api_version': current_app.config['API_VERSION'],
        'environment': current_app.config['ENVIRONMENT'],
        'endpoints': {
            'auth': '/auth',
            'jobs': '/jobs',
            'users': '/users',
            'health': '/health'
        }
    }), 200


@api_bp.route('/jobs', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_jobs():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    query = JobListing.query.filter_by(is_published=True)

    if request.args.get('company'):
        query = query.filter_by(company=request.args.get('company'))

    if request.args.get('location'):
        query = query.filter(
            JobListing.location.ilike(f"%{request.args.get('location')}%")
        )

    if request.args.get('job_type'):
        query = query.filter_by(job_type=request.args.get('job_type'))

    paginated = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        'data': [job.to_dict() for job in paginated.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': paginated.total,
            'pages': paginated.pages
        }
    }), 200


@api_bp.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    job = JobListing.query.get(job_id)

    if not job or not job.is_published:
        return jsonify({'error': 'Job not found'}), 404

    return jsonify(job.to_dict()), 200


@api_bp.route('/jobs', methods=['POST'])
@token_required
def create_job():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required_fields = ['title', 'description', 'company']

    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    try:
        job = job_service.create_job(
            title=data['title'],
            description=data['description'],
            company=data['company'],
            location=data.get('location'),
            salary_min=data.get('salary_min'),
            salary_max=data.get('salary_max'),
            job_type=data.get('job_type'),
            experience_level=data.get('experience_level'),
            skills_required=data.get('skills_required'),
            posted_by=g.user_id
        )

        logger.info(f'Job created: {job.id}')

        return jsonify({
            'message': 'Job created successfully',
            'job': job.to_dict()
        }), 201

    except Exception as e:
        logger.error(f'Job creation error: {str(e)}')
        return jsonify({'error': 'Failed to create job'}), 500


@api_bp.route('/jobs/<job_id>', methods=['PUT'])
@token_required
def update_job(job_id):
    job = JobListing.query.get(job_id)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    if str(job.posted_by) != g.user_id:
        user = User.query.get(g.user_id)

        if not user or not user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        job = job_service.update_job(job_id, data)

        return jsonify({
            'message': 'Job updated successfully',
            'job': job.to_dict()
        }), 200

    except Exception as e:
        logger.error(f'Job update error: {str(e)}')
        return jsonify({'error': 'Failed to update job'}), 500


@api_bp.route('/jobs/<job_id>', methods=['DELETE'])
@token_required
def delete_job(job_id):
    job = JobListing.query.get(job_id)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    if str(job.posted_by) != g.user_id:
        user = User.query.get(g.user_id)

        if not user or not user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403

    try:
        db.session.delete(job)
        db.session.commit()

        logger.info(f'Job deleted: {job_id}')

        return jsonify({'message': 'Job deleted successfully'}), 200

    except Exception as e:
        logger.error(f'Job deletion error: {str(e)}')
        return jsonify({'error': 'Failed to delete job'}), 500


@api_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    from app.models import UserProfile

    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    profile = UserProfile.query.filter_by(user_id=user_id).first()

    return jsonify({
        'user': user.to_dict(),
        'profile': profile.to_dict() if profile else None
    }), 200


@api_bp.route('/users/<user_id>/profile', methods=['PUT'])
@token_required
def update_user_profile(user_id):
    from app.models import UserProfile

    if user_id != g.user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        profile = user_service.update_profile(user_id, data)

        return jsonify({
            'message': 'Profile updated successfully',
            'profile': profile.to_dict()
        }), 200

    except Exception as e:
        logger.error(f'Profile update error: {str(e)}')
        return jsonify({'error': 'Failed to update profile'}), 500