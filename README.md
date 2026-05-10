# Job Match - Professional Flask 12-Factor Cloud Application

A production-ready Flask application structure following the 12-factor app methodology, cloud-native best practices, and modern Python standards.

## Features

✅ **12-Factor App Compliant**
- Configuration from environment variables
- Explicit dependency declaration
- Clean separation of concerns

✅ **Modular Architecture**
- Routes, Services, Models separation
- Blueprints for scalable routing
- Factory pattern for app creation

✅ **Database Support**
- PostgreSQL ready (psycopg2)
- SQLAlchemy ORM
- UUID primary keys
- Timestamp mixins

✅ **Caching Layer**
- Redis integration
- Cache decorators
- Session management

✅ **Testing Framework**
- pytest configuration
- Test fixtures
- Health check tests
- API endpoint tests

✅ **Docker Support**
- Multi-stage builds
- docker-compose setup
- PostgreSQL + Redis services
- Non-root user execution
- Health checks

✅ **CI/CD Pipeline**
- GitHub Actions workflow
- Automated testing
- Code quality checks (flake8, black)
- Docker image builds
- Security scanning with Trivy
- Deployment jobs

✅ **Professional Frontend**
- Jinja2 templates
- Responsive CSS
- JavaScript utilities
- Modern UI components

## Project Structure

```
job-match-folder/
├── app/                          # Application package
│   ├── __init__.py              # App factory
│   ├── config.py                # Configuration management
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   └── base.py             # Base model classes
│   ├── routes/                  # API routes (Blueprints)
│   │   ├── __init__.py
│   │   ├── health.py           # Health check endpoints
│   │   └── api.py              # API endpoints
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   └── example_service.py  # Example service
│   ├── utils/                   # Utilities
│   │   ├── __init__.py
│   │   └── decorators.py       # Custom decorators
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html           # Base template
│   │   └── index.html          # Home page
│   └── static/                  # Static files
│       ├── css/
│       │   └── style.css       # Application styles
│       └── js/
│           └── script.js       # Application JavaScript
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py             # pytest fixtures
│   └── test_health.py          # Test cases
├── .github/
│   └── workflows/
│       └── ci-cd.yml           # GitHub Actions workflow
├── Dockerfile                   # Docker image definition
├── docker-compose.yml          # Docker Compose setup
├── .dockerignore                # Docker ignore patterns
├── .env.example                 # Environment variables template
├── requirements.txt             # Python dependencies
├── wsgi.py                      # WSGI entry point (production)
├── run.py                       # Development server
├── manage.py                    # Database management
├── .gitignore                   # Git ignore patterns
└── README.md                    # Documentation
```

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (optional)

### Local Development

1. **Clone and setup**
```bash
cd job-match-folder
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. **Run locally**
```bash
# Development server
python run.py

# WSGI server (production-like)
gunicorn wsgi:app
```

5. **Access the application**
- Home: http://localhost:5000
- Health: http://localhost:5000/health
- API: http://localhost:5000/api/v1/status

### Docker Setup

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down

# Database access via pgAdmin
# URL: http://localhost:5050
# Email: admin@example.com
# Password: admin
```

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app

# Specific test file
pytest tests/test_health.py -v

# Watch mode
pytest-watch
```

## Database Management

```bash
# Create migration
flask db init
flask db migrate -m "message"
flask db upgrade

# Using manage.py
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

## Configuration

All configuration is managed through environment variables (.env file):

```env
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_NAME=job_match

# Redis
REDIS_URL=redis://localhost:6379/0

# Application
PORT=5000
APP_VERSION=1.0.0
```

## API Endpoints

### Health Checks
- `GET /health` - Full health check with dependencies
- `GET /health/live` - Kubernetes liveness probe
- `GET /health/ready` - Kubernetes readiness probe

### API v1
- `GET /api/v1/status` - API status
- `GET /api/v1/example` - Get example data
- `POST /api/v1/example` - Create example

## Development Workflow

1. **Create models** in `app/models/`
2. **Implement services** in `app/services/`
3. **Add routes** in `app/routes/`
4. **Write tests** in `tests/`
5. **Update templates** in `app/templates/`
6. **Run tests** before committing

## Production Deployment

### Docker Deployment
```bash
docker build -t job-match:latest .
docker run -d \
  --name job-match \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=$SECRET_KEY \
  job-match:latest
```

### Kubernetes Deployment
- Health checks configured (`/health/live`, `/health/ready`)
- Non-root user for security
- Graceful shutdown support
- Environment-based configuration

### Environment Variables for Production
```env
FLASK_ENV=production
SECRET_KEY=<strong-secret-key>
DB_HOST=<prod-db-host>
DB_PASSWORD=<prod-db-password>
REDIS_URL=redis://<prod-redis-host>:6379/0
SESSION_COOKIE_SECURE=true
```

## CI/CD Pipeline

GitHub Actions workflow includes:
- **Testing**: pytest with coverage
- **Linting**: flake8 and black
- **Building**: Docker image builds
- **Security**: Trivy vulnerability scanning
- **Deployment**: Automated deployments to dev/prod

## Best Practices

✅ **Security**
- Non-root Docker user
- HTTPS in production (SESSION_COOKIE_SECURE)
- Environment-based secrets
- SQL injection prevention with ORM

✅ **Performance**
- Redis caching
- Database connection pooling
- Gevent workers
- Proper indexes on models

✅ **Monitoring**
- Health check endpoints
- Structured logging
- Request logging
- Error tracking (Sentry ready)

✅ **Scalability**
- Stateless application
- Database migrations support
- Horizontal scaling ready
- Container orchestration ready

## License

MIT License

## Support

For issues and questions, please refer to the project documentation.
