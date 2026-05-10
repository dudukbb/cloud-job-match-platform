"""
WSGI entry point for production servers
Use with: gunicorn wsgi:app

Example commands:
    gunicorn wsgi:app  # Basic
    gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app  # With workers
    gunicorn -w 4 --worker-class sync -b 0.0.0.0:5000 wsgi:app  # Sync workers
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create app instance
from app import create_app

app = create_app(os.getenv('FLASK_ENV', 'production'))


# Gunicorn configuration (if using gunicorn.conf.py)
# bind = "0.0.0.0:5000"
# workers = 4
# worker_class = "sync"
# worker_tmp_dir = "/dev/shm"
# timeout = 120
# access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'


if __name__ == '__main__':
    # This is used when running with: python wsgi.py
    # For production, always use gunicorn or other WSGI server
    app.run()
