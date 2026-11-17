import os
import tempfile

import pytest

import database.db as db

# Point the data layer at a throwaway DB *before* app.py is imported,
# because app.py runs init_db() / seed_db() at import time.
_tmp_dir = tempfile.mkdtemp(prefix="spendly-test-")
db.DB_PATH = os.path.join(_tmp_dir, "test.db")

from app import app as flask_app  # noqa: E402


@pytest.fixture
def app():
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.fixture
def demo_user_id():
    return db.get_user_by_email("demo@spendly.com")["id"]


@pytest.fixture
def empty_user_id():
    """A fresh user with no expenses (unique email per test)."""
    email = f"empty-{os.urandom(4).hex()}@example.com"
    return db.create_user("Empty Person", email, "password123")


@pytest.fixture
def login(client):
    def _login(user_id, name="Test"):
        with client.session_transaction() as sess:
            sess["user_id"] = user_id
            sess["user_name"] = name
    return _login
