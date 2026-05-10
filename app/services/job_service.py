"""
Job Service
Business logic for job listing operations
"""
from app import db, cache
from app.models import JobListing
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def create_job(title, description, company, location=None, salary_min=None,
               salary_max=None, job_type=None, experience_level=None,
               skills_required=None, posted_by=None):
    """
    Create a new job listing
    
    Args:
        title: Job title
        description: Job description
        company: Company name
        location: Job location (optional)
        salary_min: Minimum salary (optional)
        salary_max: Maximum salary (optional)
        job_type: Job type (optional)
        experience_level: Required experience level (optional)
        skills_required: Required skills (optional)
        posted_by: User ID of poster (optional)
    
    Returns:
        Created JobListing object
    """
    job = JobListing(
        title=title,
        description=description,
        company=company,
        location=location,
        salary_min=salary_min,
        salary_max=salary_max,
        job_type=job_type,
        experience_level=experience_level,
        skills_required=skills_required,
        posted_by=posted_by,
        is_published=False  # Draft by default
    )
    
    db.session.add(job)
    db.session.commit()
    
    # Clear cache
    cache.delete_memoized(get_jobs)
    
    logger.info(f'Job created: {job.id}')
    return job


def get_job(job_id):
    """Get a job by ID"""
    return JobListing.query.get(job_id)


def get_jobs(page=1, per_page=20, published_only=True):
    """
    Get paginated jobs
    
    Args:
        page: Page number
        per_page: Items per page
        published_only: Only return published jobs
    
    Returns:
        Paginated JobListing query
    """
    query = JobListing.query
    
    if published_only:
        query = query.filter_by(is_published=True)
    
    return query.paginate(page=page, per_page=per_page, error_out=False)


def update_job(job_id, data):
    """
    Update a job listing
    
    Args:
        job_id: Job ID
        data: Dictionary of fields to update
    
    Returns:
        Updated JobListing object
    """
    job = JobListing.query.get(job_id)
    
    if not job:
        raise ValueError('Job not found')
    
    # Update allowed fields
    allowed_fields = [
        'title', 'description', 'company', 'location',
        'salary_min', 'salary_max', 'job_type', 'experience_level',
        'skills_required', 'is_published'
    ]
    
    for key, value in data.items():
        if key in allowed_fields and value is not None:
            setattr(job, key, value)
    
    job.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Clear cache
    cache.delete_memoized(get_jobs)
    
    logger.info(f'Job updated: {job_id}')
    return job


def publish_job(job_id):
    """Publish a job listing"""
    job = JobListing.query.get(job_id)
    if job:
        job.is_published = True
        job.updated_at = datetime.utcnow()
        db.session.commit()
        cache.delete_memoized(get_jobs)
        logger.info(f'Job published: {job_id}')
    return job


def unpublish_job(job_id):
    """Unpublish a job listing"""
    job = JobListing.query.get(job_id)
    if job:
        job.is_published = False
        job.updated_at = datetime.utcnow()
        db.session.commit()
        cache.delete_memoized(get_jobs)
        logger.info(f'Job unpublished: {job_id}')
    return job


def delete_job(job_id):
    """Delete a job listing"""
    job = JobListing.query.get(job_id)
    if job:
        db.session.delete(job)
        db.session.commit()
        cache.delete_memoized(get_jobs)
        logger.info(f'Job deleted: {job_id}')
    return True


def search_jobs(query, company=None, location=None, job_type=None):
    """
    Search for jobs
    
    Args:
        query: Search query
        company: Filter by company
        location: Filter by location
        job_type: Filter by job type
    
    Returns:
        Query results
    """
    jobs = JobListing.query.filter_by(is_published=True)
    
    if query:
        jobs = jobs.filter(
            (JobListing.title.ilike(f'%{query}%')) |
            (JobListing.description.ilike(f'%{query}%'))
        )
    
    if company:
        jobs = jobs.filter_by(company=company)
    
    if location:
        jobs = jobs.filter(JobListing.location.ilike(f'%{location}%'))
    
    if job_type:
        jobs = jobs.filter_by(job_type=job_type)
    
    return jobs.all()