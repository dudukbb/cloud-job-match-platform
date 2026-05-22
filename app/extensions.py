from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
import redis

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()

login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"

# Redis client — initialised in create_app
redis_client: redis.Redis = None  # type: ignore[assignment]
