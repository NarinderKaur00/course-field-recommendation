"""Pytest fixtures for the portal."""
import os
import sys

import pytest

PORTAL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PORTAL_DIR)

import app as A  # noqa: E402
import store  # noqa: E402
import ai_assist  # noqa: E402

# Tests run fully offline: never call a real LLM even if a key is in .env
ai_assist.PROVIDER = "none"


@pytest.fixture
def app_module():
    return A


@pytest.fixture
def client():
    """A fresh test client backed by an in-memory mongomock database."""
    store.configure(use_mock=True)
    store.reset()
    # Pin admin creds to known test values so tests never depend on a local .env
    A.ADMIN_USER, A.ADMIN_PASS = "admin", "admin123"
    A.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with A.app.test_client() as c:
        yield c


@pytest.fixture
def auth_client(client):
    """A client already registered and logged in as a student."""
    client.post("/register", data={"name": "Test User", "email": "t@test.com",
                                    "password": "1234", "confirm": "1234", "consent": "1"},
                follow_redirects=True)
    client.post("/login", data={"email": "t@test.com", "password": "1234"},
                follow_redirects=True)
    return client


@pytest.fixture
def admin_client(client):
    """A client logged in as admin."""
    client.post("/admin/login", data={"username": A.ADMIN_USER, "password": A.ADMIN_PASS},
                follow_redirects=True)
    return client


def median_marks():
    """Default marks payload (used to trigger a recommendation)."""
    feats = A.BUNDLE["feature_columns"]
    return {c: str(round(A.BUNDLE["feature_medians"][c])) for c in feats}
