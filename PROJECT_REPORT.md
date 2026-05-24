# Cloud Job Match Platform
## Course Project Report: 12-Factor Cloud Application

## Title Page

| Item | Details |
|---|---|
| Project Name | Cloud Job Match Platform |
| Course Project | 12-Factor Cloud Application |
| Team Size | [Solo / Duo / Team of 3] |
| Student Name(s) | [Student 1], [Student 2], [Student 3] |
| Student ID(s) | [ID 1], [ID 2], [ID 3] |
| Department/Program | [Program Name] |
| Instructor | [Instructor Name] |
| GitHub Repository Link | [Add repository URL] |
| Live Demo Link | [Add live demo URL] |
| Submission Date | [Add date] |

---

## 1. Abstract
In this project, we developed Cloud Job Match Platform, a cloud-based recruitment system that supports role-based hiring workflows and skill-driven candidate evaluation. We implemented the backend using Flask and SQLAlchemy, persistent data storage with PostgreSQL, performance caching with Redis, containerized deployment with Docker, and continuous integration and delivery with GitHub Actions.

Our platform includes resume upload, PDF and DOCX text extraction, keyword-based skill identification, and automated compatibility scoring between applicant skills and job requirements. We designed the application according to 12-factor principles by externalizing configuration, treating databases and caches as backing services, emitting logs to stdout, and maintaining deployment portability for cloud environments such as Render.

## 2. Introduction
Recruitment systems often fail at quickly identifying relevant applicants. Job seekers struggle to find suitable openings, while employers spend significant time manually screening resumes and comparing skills against job requirements.

To address this problem, we implemented a cloud-native web application that combines traditional job board functionality with automated skill-based matching. Our project integrates user authentication, job publishing, resume-assisted profiling, and employer-side application review into a single, deployable 12-factor platform.

## 3. Project Objectives
The objectives of our project were to:
- Build a cloud-deployed 12-factor application.
- Implement secure authentication and role-based access control.
- Enable employers to create and manage job postings.
- Enable job seekers to browse listings and submit applications.
- Support CV upload and automated skill extraction.
- Compute skill-based match percentages.
- Provide an employer decision workflow for applications.
- Integrate PostgreSQL, Redis, Docker, CI/CD, logging, and deployment best practices.

## 4. System Features
Our platform provides the following features:
- User authentication: registration, login, and logout.
- User roles: employer and job seeker.
- Employer job management: create, edit, delete, and manage listings.
- Job browsing with keyword search, type filtering, and pagination.
- Application submission flow for job seekers.
- CV upload support in application forms.
- Resume parsing pipeline:
  - PDF extraction using pypdf.
  - DOCX extraction via XML parsing from DOCX package content.
  - Graceful fallback when extraction fails.
- Skill extraction based on common technical keywords.
- Compatibility analysis:
  - Match percentage.
  - Matched skills list.
  - Missing skills list.
- Employer review dashboard restricted to owned job posts.
- Secure resume view and download route with authorization checks.
- Application decision workflow:
  - Pending.
  - Under Review.
  - Accepted.
  - Rejected.
- My Applications view for job seekers with status visibility.
- Health endpoint for dependency checks.

## 5. 12-Factor App Compliance
Our project follows the 12-factor methodology as described below.

### I. Codebase
We maintain a single version-controlled codebase and deploy it to multiple environments (local, CI, and cloud).

### II. Dependencies
We declare dependencies explicitly in requirements files and isolate runtime environments using virtual environments and Docker images.

### III. Config
We keep configuration in environment variables, including secrets, service URLs, logging level, and runtime options.

### IV. Backing Services
We treat PostgreSQL and Redis as attached resources referenced through environment-provided connection strings.

### V. Build, Release, Run
We separate build and runtime concerns with a multi-stage Dockerfile and environment-specific runtime configuration.

### VI. Processes
We run the web service as a stateless process and store persistent data in external services.

### VII. Port Binding
We expose and bind to a configurable network port at runtime for cloud compatibility.

### VIII. Concurrency
We support process-level concurrency through configurable Gunicorn workers and container scaling.

### IX. Disposability
We support fast startup and controlled shutdown behavior, and we expose health checks for orchestration systems.

### X. Dev/Prod Parity
We reduce environment drift by using containerized workflows and shared dependency definitions across development, CI, and production.

### XI. Logs
We emit structured logs to stdout and stderr, enabling integration with platform log aggregation.

### XII. Admin Processes
We can run operational tasks as one-off commands in the same release environment.

## 6. Technology Stack

### Backend
- Python
- Flask
- SQLAlchemy (Flask-SQLAlchemy)
- Flask-Login
- Flask-Bcrypt
- Flask-WTF

### Database
- PostgreSQL

### Caching
- Redis

### Frontend
- Jinja2 templates
- Bootstrap 5
- Bootstrap Icons

### DevOps
- Docker
- Docker Compose
- GitHub Actions
- Render

### Testing
- Pytest
- pytest-flask
- pytest-timeout

## 7. Cloud Deployment
We designed our platform for cloud deployment on Render and similar providers.

Deployment characteristics:
- The application runs behind Gunicorn and binds to a platform-provided port.
- PostgreSQL is connected through DATABASE_URL.
- Redis is connected through REDIS_URL.
- Secret and runtime settings are injected as environment variables.
- Health monitoring is available via the health endpoint.
- CI and image publishing are automated through GitHub Actions and can be connected to auto-deploy workflows.

## 8. Database Design
Our data model is centered on three entities.

### User
- Core fields: id, username, email, password hash, employer flag, and skills.
- Behavioral role:
  - Employers manage job posts and review applications.
  - Job seekers apply to jobs and receive match insights.

### Job
- Core fields: title, company, location, description, required skills, salary range, job type, and active flag.
- Each job belongs to one employer.

### Application
- Core fields: cover letter, resume metadata, status, applicant reference, and job reference.
- One applicant can submit only one application per job.
- Status lifecycle supports Pending, Under Review, Accepted, and Rejected.

## 9. Redis Caching
We implemented Redis caching for job listing responses to improve read performance.

Key behaviors:
- Cache keys include page and filter context.
- Cached payload includes records and pagination metadata.
- Cache invalidation runs after create, edit, or delete operations on jobs.
- Redis failures do not break listing behavior because our project falls back to PostgreSQL queries.

## 10. AI-Assisted Skill Matching
Our matching module combines profile and resume information with job requirements.

Processing pipeline:
- User skill source:
  - Manual skills entered during registration.
  - Skills extracted from uploaded resumes.
- Resume parsing:
  - PDF parsing using pypdf.
  - DOCX parsing using ZIP and XML extraction.
- Skill extraction:
  - Keyword detection for common technical terms.
- Matching algorithm:
  - Normalize skill sets by splitting comma-separated values.
  - Convert to lowercase and trim whitespace.
  - Compute match_score as matched skills divided by required skills times 100.
  - Produce matched_skills and missing_skills lists.

Presentation:
- Job list cards show score and matched or missing sets when data is available.
- Job detail page shows a compatibility summary for job seekers.

## 11. Employer Application Review Workflow
We implemented an employer-only review workflow with ownership checks.

Workflow elements:
- Employers can view applications only for jobs they own.
- Employers can access candidate profile details and matching metrics.
- Employers can open uploaded resumes through a protected file route.
- Employers can update status to Under Review, Accepted, or Rejected.
- Job seekers can monitor updated statuses on the My Applications page.

## 12. Security Considerations
We implemented multiple security controls:
- Password hashing with Flask-Bcrypt.
- CSRF protection on POST forms.
- Login-required route protection.
- Role-based authorization rules for employer and job seeker actions.
- Ownership validation for decision updates and resume access.
- Secure file name handling for uploaded resumes.
- Environment-driven secret management.

## 13. Testing and Validation
Our project uses Pytest for automated validation.

Current test coverage includes:
- Health endpoint behavior.
- Job listing access.
- Registration and login flows.
- Protected route redirection.
- Redis fallback behavior.

Current automated result:
- 7 tests passed.

Additional validation:
- We conducted manual end-to-end checks for employer and job seeker workflows, including resume upload and application decisions.

## 14. CI/CD Pipeline
We implemented two GitHub Actions workflows.

### CI Workflow
- Triggered by pushes and pull requests.
- Installs runtime and development dependencies.
- Runs tests with timeout protection.
- Builds Docker image as a verification step.

### CD Workflow
- Builds and publishes Docker images to GHCR.
- Generates tags for branch, commit SHA, and releases.
- Supports integration with Render deployment triggers.

## 15. Logging and Monitoring
Our observability approach includes:
- Structured logging configured in the Flask application factory.
- Stdout and stderr log streaming for cloud runtime visibility.
- Dependency-aware health endpoint for PostgreSQL and Redis.
- Safe logging of Redis degradation without disrupting user flows.
- Platform-level monitoring support through Render logs.

### Prometheus Monitoring
We integrated lightweight Prometheus-based monitoring to provide observability without breaking the existing architecture.

**Why Prometheus:**
- Provides production-grade metrics collection and time-series storage compatibility.
- Standard monitoring solution for cloud-native applications.
- Lightweight overhead with automatic metric tracking.

**What `/metrics` provides:**
- HTTP request count per endpoint, method, and status code.
- Request latency (response time distribution).
- Response status code distribution (2xx, 3xx, 4xx, 5xx).
- All metrics follow OpenMetrics format compatible with Prometheus scraping.

**How it improves observability:**
- Enables detection of performance degradation or error spikes.
- Tracks user-facing SLOs like request latency percentiles.
- Supports alerting on critical metrics (e.g., error rate > 5%).
- Integrates seamlessly with existing Prometheus or cloud-native stacks.

**Integration notes:**
- The `/metrics` endpoint is automatically exposed and requires no configuration changes.
- Application works normally if Prometheus is not actively scraping.
- Metrics collection has minimal CPU and memory overhead.
- Compatible with Render's monitoring integrations and third-party APM tools.

## 16. Demo Scenario
We present the system with the following sequence:
1. Open the live application.
2. Register and log in as an employer.
3. Create a job post with required skills.
4. Log out.
5. Register and log in as a job seeker.
6. Browse jobs and review match indicators.
7. Open job detail and submit an application with a resume.
8. Let the platform extract skills and update the seeker profile.
9. Log in as employer and open the review dashboard.
10. Review match details and open the uploaded resume.
11. Set status to Under Review, Accepted, or Rejected.
12. Log in as job seeker and verify updated status in My Applications.

## 17. Challenges and Solutions

### Merge conflicts and Git rebase issues
- Challenge: Continuous integration of multiple updates caused branch conflicts.
- Solution: We used controlled rebase conflict resolution and explicit staging practices.

### Template consistency and rendering errors
- Challenge: Dynamic template updates increased risk of syntax and context mismatches.
- Solution: We applied incremental edits and validated route-template data contracts.

### Redis availability and graceful degradation
- Challenge: Cache outages could impact user-facing routes.
- Solution: We wrapped cache operations and preserved database fallback behavior.

### Database compatibility during feature evolution
- Challenge: New columns had to work with existing database states.
- Solution: We implemented additive schema compatibility updates at startup.

### CV parsing reliability
- Challenge: Uploaded files may be malformed or text extraction may fail.
- Solution: We handled extraction failures gracefully and preserved application submission.

### Cloud configuration parity
- Challenge: Environment differences can cause deployment drift.
- Solution: We standardized environment-based configuration and CI validation steps.

## 18. Conclusion
We successfully implemented a practical 12-factor cloud application that combines secure authentication, role-based workflows, PostgreSQL persistence, Redis caching, CI/CD automation, containerized deployment, health monitoring, Prometheus observability, and AI-assisted skill matching.

Our project meets the core university requirements while remaining maintainable and extensible for production-oriented enhancements.

## 19. Future Improvements
Planned future enhancements include:
- More advanced NLP-based resume parsing and semantic matching.
- Email notifications for application and status events.
- Administrative dashboard and moderation controls.
- Metrics-based monitoring dashboard and alerting.
- Persistent cloud object storage for resumes.
- Advanced ranking algorithms that incorporate skill weights and experience.

## 20. Evaluation Mapping

| Requirement | Project Mapping |
|---|---|
| Language | Python Flask |
| Database | PostgreSQL |
| Deployment | Render cloud provider |
| CI/CD | GitHub Actions |
| Caching | Redis |
| Monitoring | Health endpoint and Render logs |
| Logging | Flask logger and Render logs |
| GitHub repository | Available |
| Demo video | To be submitted |
| Project report | PROJECT_REPORT.md |

---

## Appendix: Key Repository Components Reviewed
- Application factory and configuration: app/__init__.py, config.py, run.py
- Data models: app/models.py
- Core routes: app/routes/auth.py, app/routes/jobs.py, app/routes/applications.py, app/routes/health.py
- Skill matching utilities: app/skill_matching.py
- Templates: app/templates
- Tests: tests/conftest.py, tests/test_app.py
- Containerization: Dockerfile, docker-compose.yml
- CI/CD workflows: .github/workflows/ci.yml, .github/workflows/cd.yml
- Dependency manifests: requirements.txt, requirements-dev.txt
