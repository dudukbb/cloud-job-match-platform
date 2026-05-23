import pytest
import os
from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    # Force an isolated SQLite database for deterministic, fast CI test runs.
    db_dir = tmp_path_factory.mktemp("test_db")
    test_db_path = db_dir / "app.db"

    previous_test_db_url = os.environ.get("TEST_DATABASE_URL")
    os.environ["TEST_DATABASE_URL"] = f"sqlite:///{test_db_path.as_posix()}"

    application = create_app("testing")
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()
        _db.engine.dispose()

    if previous_test_db_url is None:
        os.environ.pop("TEST_DATABASE_URL", None)
    else:
        os.environ["TEST_DATABASE_URL"] = previous_test_db_url


@pytest.fixture()
def client(app):
    return app.test_client()
