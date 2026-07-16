"""Shared fixtures for the DevLog backend test suite.

Test database choice: a REAL PostgreSQL database (devlog_test), not SQLite.
Why: the Post model uses postgresql.ARRAY for tags (plus a GIN index in prod);
SQLite has no ARRAY type, so the schema wouldn't even create. Testing against
the same engine as production also exercises real dialect behavior (timezone
timestamps, composite PKs) instead of a lookalike. The cost — needing a local
postgres — is zero here because dev already runs one.

IMPORTANT: DATABASE_URL is overridden via environment variable BEFORE any app
import, because pydantic-settings gives real env vars precedence over .env.
"""

import os

os.environ["DATABASE_URL"] = "postgresql://devlog:devlog@localhost:5432/devlog_test"
os.environ["GROQ_API_KEY"] = "test-key-never-used"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.services import ai_service  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    """Create all tables once per test session, drop them at the end."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(autouse=True)
def _clean_tables():
    """Truncate all tables between tests so every test starts from zero."""
    yield
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE follows, posts, users RESTART IDENTITY CASCADE"))


@pytest.fixture(autouse=True)
def mock_ai(monkeypatch):
    """Never call a real LLM in tests. Returns canned summary/tags."""
    monkeypatch.setattr(
        ai_service, "summarize_post", lambda content: "A mocked TL;DR of the post."
    )
    monkeypatch.setattr(
        ai_service, "generate_tags", lambda content: ["testing", "python", "mocked"]
    )


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def register_and_login(client: TestClient, username: str = "tester") -> dict[str, str]:
    """Register a user, log in, and return Authorization headers."""
    client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "password123",
        },
    )
    response = client.post(
        "/api/auth/login",
        data={"username": username, "password": "password123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers(client) -> dict[str, str]:
    """Headers for a default authenticated user ('tester')."""
    return register_and_login(client)


@pytest.fixture
def db_session():
    """Direct DB access for assertions that bypass the API."""
    session = SessionLocal()
    yield session
    session.close()
