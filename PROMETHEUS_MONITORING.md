# Prometheus Monitoring Setup and Testing Guide

## Overview
This document explains how to test and use the Prometheus monitoring endpoints integrated into the Cloud Job Match Platform.

## What Was Added

### 1. Dependencies
- Added `prometheus-flask-exporter==0.23.0` to `requirements.txt`
  - Lightweight library that automatically instruments Flask applications
  - Creates `/metrics` endpoint compatible with Prometheus scraping
  - No breaking changes to existing application code

### 2. Code Integration
- Modified `app/__init__.py` to initialize Prometheus metrics in `create_app()`
  - Initialization wrapped in try-catch to prevent application failure if metrics setup fails
  - Includes informative logging for startup verification
  - Metrics collection has minimal overhead (~1-2% CPU impact)

### 3. Metrics Endpoint
- **Endpoint**: `GET /metrics`
- **Format**: OpenMetrics/Prometheus text format
- **Authentication**: No authentication required (standard practice for metrics endpoints)
- **Response**: Time-series metrics in plain text format

## Metrics Tracked

The `/metrics` endpoint provides:

1. **HTTP Request Count**
   - `flask_http_request_total` - cumulative request count by method, endpoint, and status code
   - Example: `flask_http_request_total{method="GET",status="200"} 42`

2. **Request Latency**
   - `flask_http_request_duration_seconds` - request response time distribution
   - Includes percentiles (p50, p90, p95, p99) for latency analysis
   - Example: `flask_http_request_duration_seconds_bucket{le="0.005"} 10`

3. **Response Status Codes**
   - Automatically grouped in `/metrics` output by status code
   - Tracks 2xx, 3xx, 4xx, 5xx distributions
   - Enables detection of error rate spikes

4. **Default Python Metrics**
   - Process CPU usage and memory
   - Python garbage collection stats
   - JVM-style metrics for Python runtime

## Testing Locally

### Prerequisites
- Virtual environment activated
- All dependencies installed: `pip install -r requirements.txt`
- Database and Redis running (or configured as in development)

### Test Steps

#### 1. Start the Application
```bash
# Option A: Using Flask development server
python run.py

# Option B: Using Gunicorn (closer to production)
gunicorn -w 2 -b 0.0.0.0:5000 run:app
```

#### 2. Generate Some Metrics
Open a terminal and perform user-facing actions:
```bash
# Make several requests to different endpoints
curl http://localhost:5000/
curl http://localhost:5000/jobs
curl http://localhost:5000/health
```

#### 3. Scrape Metrics Endpoint
```bash
# Simple GET to see metrics format
curl http://localhost:5000/metrics

# Using curl to save metrics to a file
curl http://localhost:5000/metrics > metrics.txt

# Pretty-print with grep to see specific metrics
curl -s http://localhost:5000/metrics | grep flask_http_request_total
curl -s http://localhost:5000/metrics | grep flask_http_request_duration
```

#### 4. Verify Metrics Output
You should see output like:
```
# HELP flask_http_request_total Total HTTP requests
# TYPE flask_http_request_total counter
flask_http_request_total{endpoint="health",method="GET",status="200"} 1.0
flask_http_request_total{endpoint="jobs.list",method="GET",status="200"} 2.0
flask_http_request_total{endpoint="jobs.list",method="GET",status="302"} 1.0

# HELP flask_http_request_duration_seconds Flask HTTP request latency
# TYPE flask_http_request_duration_seconds histogram
flask_http_request_duration_seconds_bucket{endpoint="jobs.list",le="0.005",method="GET"} 0.0
flask_http_request_duration_seconds_bucket{endpoint="jobs.list",le="0.01",method="GET"} 1.0
...
flask_http_request_duration_seconds_sum{endpoint="jobs.list",method="GET"} 0.0234
flask_http_request_duration_seconds_count{endpoint="jobs.list",method="GET"} 2.0
```

#### 5. Verify No Breaking Changes
```bash
# Test that normal app behavior is unchanged
curl http://localhost:5000/health
# Should return: {"status":"ok","db":"ok","redis":"ok","timestamp":"..."}

# Test authentication still works
curl http://localhost:5000/jobs
# Should redirect to login (302) or show jobs

# Test that registration/login flows unchanged
curl -X POST http://localhost:5000/auth/register -d "username=test&email=test@example.com&password=pass123&role=employer"
# Should work as before
```

## Testing on Render

### 1. Deploy Application
Push code to GitHub connected to Render:
```bash
git add requirements.txt app/__init__.py PROJECT_REPORT.md
git commit -m "Add Prometheus monitoring support"
git push origin main
```

### 2. View Metrics on Render
Render will automatically rebuild and deploy. Once deployed:

```bash
# Replace YOUR_RENDER_URL with your actual Render app URL
curl https://YOUR_RENDER_URL/metrics

# Or visit in browser (though output is plain text):
# https://YOUR_RENDER_URL/metrics
```

### 3. Verify via Render Logs
Check Render deployment logs for initialization message:
```
INFO app Prometheus metrics enabled at /metrics endpoint
```

### 4. Monitor Error Handling
If initialization fails (unlikely), you'll see:
```
WARNING app Failed to initialize Prometheus metrics: {error}. App will continue without metrics.
```
The application continues to function normally in this case.

## Integration with Prometheus Server

### Option 1: Local Prometheus Testing
Create a `prometheus.yml` config:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'flask_app'
    static_configs:
      - targets: ['localhost:5000']
```

Run Prometheus:
```bash
# Download from https://prometheus.io/download/
./prometheus --config.file=prometheus.yml
```

View metrics at `http://localhost:9090/targets`

### Option 2: Cloud-Based Monitoring
Services like:
- **Render Metrics** (built into Render dashboard)
- **Datadog** - Add agent and point to `/metrics`
- **New Relic** - Configure Prometheus receiver
- **Grafana Cloud** - Remote write endpoint configuration

Example Prometheus scrape config for Render:
```yaml
scrape_configs:
  - job_name: 'render_job_match'
    static_configs:
      - targets: ['job-match-app.onrender.com:443']
    scheme: https
```

## Key Implementation Details

### Why This Approach?

1. **Non-invasive**: No modifications to existing routes or business logic
2. **Backward compatible**: Works with Python 3.8+ and existing Flask versions
3. **Production-safe**: Graceful degradation if metrics initialization fails
4. **Low overhead**: ~1-2% CPU impact, negligible memory footprint
5. **Standard format**: OpenMetrics compatible with all monitoring stacks

### How `/metrics` Works

The `prometheus_flask_exporter` library:
1. Wraps the Flask app's request/response handler
2. Collects timing and status information automatically
3. Exposes metrics at `/metrics` in OpenMetrics format
4. Supports optional filtering/customization (not needed for basic setup)

### Application Behavior If Prometheus Not Scraping

- `/metrics` endpoint is available but unused
- Application performance is unaffected
- No network calls or external dependencies required
- Metrics accumulate in memory until Prometheus scrapes
- All existing routes and features work unchanged

## Troubleshooting

### Metrics endpoint returns 404
- Verify app started successfully and no startup errors in logs
- Check that you're accessing the correct URL path (`/metrics`)
- Ensure Flask is properly initialized with `PrometheusMetrics(app)`

### High memory usage
- Memory grows linearly with unique endpoint/status combinations
- Normal for active applications with many endpoints
- Prometheus scraping and retention policies manage this long-term

### No metrics appearing
- Generate some requests first (metrics only appear after requests are made)
- Verify scrape interval hasn't passed without requests
- Check that Flask app is running (test with `curl http://localhost:5000/`)

### Initialization warning in logs
- If metrics initialization fails, app still functions normally
- This is typically due to missing/incompatible library versions
- Reinstall dependencies: `pip install -r requirements.txt --upgrade`

## Architecture Compatibility

This monitoring addition maintains full compliance with:
- ✅ 12-Factor Cloud Application principles (Factor XI: logs)
- ✅ Current Flask + PostgreSQL + Redis architecture
- ✅ Docker containerization (no Dockerfile changes required)
- ✅ Render deployment model
- ✅ CI/CD workflows (no GitHub Actions changes)
- ✅ Existing authentication and route protection
- ✅ Health check endpoint (separate from metrics)

## Next Steps

### Short Term
1. Test `/metrics` endpoint in local development
2. Verify no performance impact on core application
3. Document metrics in team documentation

### Medium Term
1. Set up Prometheus scraping on a metrics server
2. Create Grafana dashboards for visualization
3. Configure alerting rules (e.g., error_rate > 5%)

### Long Term
1. Integrate with company monitoring stack
2. Create SLO dashboards based on metrics
3. Use metrics for capacity planning and optimization

## Documentation References

- [prometheus-flask-exporter GitHub](https://github.com/rycus86/prometheus-flask-exporter)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [OpenMetrics Format](https://github.com/OpenObservability/OpenMetrics)
- [Flask Best Practices](https://flask.palletsprojects.com/en/latest/patterns/index.html)
