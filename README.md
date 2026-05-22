# Cloud Job Match Platform

A production-ready, 12-factor Flask application for job posting and matching — containerised with Docker, backed by PostgreSQL and Redis, and deployable to any cloud provider.

---

## Features

| Feature | Details |
|---|---|
| **Auth** | Register / login / logout with bcrypt-hashed passwords |
| **Job Listings** | Full CRUD (employers only), search & filter, paginated |
| **Applications** | Job seekers apply with cover letter; employers manage status |
| **Redis Cache** | Job listing pages cached with configurable TTL |
| **Health Check** | `GET /health` — checks DB + Redis liveness |
| **Structured Logging** | Timestamped logs emitted to stdout (Factor XI) |
| **12-Factor Ready** | Config in env, stateless processes, dev/prod parity |

---

## Quick Start (Docker)

```bash
# 1. Clone and configure
git clone <your-repo-url>
cd job-match-folder
cp .env.example .env          # edit SECRET_KEY at minimum

# 2. Start all services
docker compose up --build

# 3. Visit the app
open http://localhost:5000
```

Stop everything:

```bash
docker compose down            # keeps postgres volume
docker compose down -v         # also removes postgres volume
```

---

## Local Development (without Docker)

### Prerequisites

- Python 3.12+
- PostgreSQL 14+ running locally
- Redis 7+ running locally

### Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements-dev.txt

cp .env.example .env
# Edit .env — set DATABASE_URL and REDIS_URL to your local services

flask --app run:app run --debug
```

The app will be available at `http://localhost:5000`.

### Running Tests

```bash
pytest tests/ -v
```

---

## Project Structure

```
job-match-folder/
├── app/
│   ├── __init__.py          # Application factory (Factor I)
│   ├── extensions.py        # Flask extensions (db, login, bcrypt, redis)
│   ├── models.py            # SQLAlchemy models (User, Job, Application)
│   ├── routes/
│   │   ├── auth.py          # /auth/* — register, login, logout
│   │   ├── jobs.py          # /jobs/* — CRUD + Redis-cached listings
│   │   ├── applications.py  # /applications/* — apply, my-apps, status
│   │   └── health.py        # /health — liveness probe
│   └── templates/
│       ├── base.html        # Bootstrap 5 layout
│       ├── auth/            # login.html, register.html
│       ├── jobs/            # list.html, detail.html, create.html, edit.html
│       └── applications/    # my_applications.html
├── tests/
│   ├── conftest.py
│   └── test_app.py
├── .github/
│   └── workflows/ci.yml     # GitHub Actions: test + docker build
├── config.py                # Development / Testing / Production configs
├── run.py                   # WSGI entry point
├── Dockerfile               # Multi-stage build (builder + slim runtime)
├── docker-compose.yml       # web + postgres + redis services
├── requirements.txt
├── requirements-dev.txt
├── .env.example
└── .gitignore
```

---

## Environment Variables (Factor III)

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | *(required)* | Flask session signing key |
| `DATABASE_URL` | `postgresql://...@localhost/jobmatch` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `CACHE_TTL` | `300` | Job listing cache lifetime in seconds |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `JOBS_PER_PAGE` | `10` | Pagination size |
| `SESSION_LIFETIME` | `3600` | Remember-me session duration (seconds) |
| `FLASK_ENV` | `development` | `development`, `testing`, or `production` |
| `PORT` | `5000` | HTTP port used by Gunicorn in containers |
| `WEB_CONCURRENCY` | `2` | Gunicorn worker count |
| `GUNICORN_TIMEOUT` | `60` | Gunicorn request timeout (seconds) |
| `AUTO_CREATE_TABLES` | `true` | Auto-create DB schema on startup |
| `TRUST_PROXY` | `false` | Trust reverse-proxy headers (`X-Forwarded-*`) |
| `REQUIRE_STRONG_SECRET` | `false` | Fail startup if `SECRET_KEY` is insecure |

---

## Cloud Deployment

### Heroku

```bash
heroku create my-job-match
heroku addons:create heroku-postgresql:essential-0
heroku addons:create heroku-redis:mini
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set FLASK_ENV=production
git push heroku main
```

### AWS / GCP / Azure (Container)

1. Push the Docker image to your container registry (ECR / Artifact Registry / ACR).
2. Create a managed PostgreSQL instance and Redis instance.
3. Deploy the image via ECS / Cloud Run / ACI.
4. Inject environment variables via the platform's secrets / env-var mechanism.
5. Point the load-balancer health check at `GET /health`.

### Kubernetes (minimal)

```yaml
# Set DATABASE_URL and REDIS_URL as Kubernetes Secrets, then:
kubectl create secret generic jobmatch-secrets \
  --from-literal=SECRET_KEY=<value> \
  --from-literal=DATABASE_URL=<value> \
  --from-literal=REDIS_URL=<value>

kubectl apply -f k8s/   # add your Deployment + Service manifests
```

---

## The 12 Factors — How This App Addresses Each

| # | Factor | Implementation |
|---|---|---|
| I | **Codebase** | Single repo, multiple deploys via environment |
| II | **Dependencies** | `requirements.txt`; isolated in `venv` or Docker layer |
| III | **Config** | All config via environment variables / `.env` |
| IV | **Backing services** | PostgreSQL & Redis declared as attached resources in `docker-compose.yml` |
| V | **Build, release, run** | Docker multi-stage build separates build from runtime |
| VI | **Processes** | Stateless Flask process; sessions stored in signed cookies |
| VII | **Port binding** | Gunicorn binds `0.0.0.0:$PORT`; exposed via Docker |
| VIII | **Concurrency** | Scale via Gunicorn workers (`--workers`) or container replicas |
| IX | **Disposability** | Fast startup; graceful shutdown via Gunicorn signals |
| X | **Dev/prod parity** | Same Docker image in CI and production |
| XI | **Logs** | Structured logs written to stdout; no log files |
| XII | **Admin processes** | `flask shell` / `flask db` for one-off tasks |

---

## CI / CD

GitHub Actions CI workflow (`.github/workflows/ci.yml`) runs on every push to `main`/`develop` and pull requests to `main`:

1. Spins up PostgreSQL and Redis service containers.
2. Installs `requirements-dev.txt`.
3. Runs `pytest tests/ -v`.
4. Builds the Docker image to verify the `Dockerfile`.

GitHub Actions CD workflow (`.github/workflows/cd.yml`) runs on pushes to `main`, version tags (`v*`), and manual triggers:

1. Logs in to GitHub Container Registry (`ghcr.io`).
2. Builds the Docker image using Buildx.
3. Publishes tags for branch, commit SHA, and release tags.

---

## License

MIT
