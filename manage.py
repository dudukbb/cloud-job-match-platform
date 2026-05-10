"""
Database management script
Supports initialization, migration, and management tasks
"""
import os
import sys
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db


app = create_app(os.getenv('FLASK_ENV', 'development'))
migrate = Migrate(app, db)
manager = Manager(app)

# Add migration commands
manager.add_command('db', MigrateCommand)


@manager.command
def create_admin():
    """Create an admin user"""
    pass


@manager.command
def seed_database():
    """Seed database with initial data"""
    pass


if __name__ == '__main__':
    manager.run()
