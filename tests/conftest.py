"""Session-wide safety. The DB guard runs before ANY test is collected to run."""
import os

import pytest

from tests.keel_db_guard import (
    UnsafeDatabaseError,
    check_database_is_disposable,
    postgres_probe,
    require_verified,
)

_MODE_KEY = pytest.StashKey[str]()


def pytest_sessionstart(session: pytest.Session) -> None:
    try:
        mode = check_database_is_disposable(os.environ, postgres_probe)
    except UnsafeDatabaseError as exc:
        pytest.exit(f"KEEL DB GUARD REFUSED: {exc}", returncode=3)
    session.config.stash[_MODE_KEY] = mode


@pytest.fixture(scope="session")
def db_url(request: pytest.FixtureRequest) -> str:
    """The ONLY sanctioned way for a test to reach a database."""
    require_verified(request.config.stash[_MODE_KEY])
    return os.environ["DATABASE_URL"]


@pytest.fixture
def api_key(monkeypatch: pytest.MonkeyPatch) -> str:
    key = "sgmdk-test-key-7f3a91"  # distinctive: no correct server default could equal it
    monkeypatch.setenv("STOCKGRADER_API_KEY", key)
    return key
