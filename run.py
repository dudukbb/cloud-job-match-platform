"""
Development server runner
Use this for local development only.
"""

import os
from dotenv import load_dotenv

# Load environment variables before importing app
load_dotenv()

from app import create_app

app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    print("Starting Job Match Application")
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"Database URL: {os.getenv('DATABASE_URL')}")
    print(f"Redis URL: {os.getenv('REDIS_URL')}")
    print(f"\nStarting development server on http://127.0.0.1:{os.getenv('PORT', 5000)}")
    print("Press CTRL+C to quit\n")

    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("DEBUG", "True").lower() == "true",
        use_reloader=True
    ) 