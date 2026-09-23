"""Hermetic tests for the migration runner (D-021).

These need no database. Everything here is file discovery, ordering, checksum
and the transaction-control refusal — the parts that must be right *before* a
connection is opened, which is exactly why they can be tested in the gate.

The parts that need a real Postgres (apply, verify-then-rollback-to-savepoint,
advisory lock) are non-hermetic and live in the testplan's non-hermetic track.
A hermetic green here is not evidence that a migration applies.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("migrate", _REPO / "db" / "migrate.py")
migrate = importlib.util.module_from_spec(_spec)
sys.modules["migrate"] = migrate
_spec.loader.exec_module(migrate)


def _write(d: Path, name: str, body: str = "CREATE TABLE t (x int);") -> Path:
    p = d / name
    p.write_text(body, encoding="utf-8")
    return p


def _with_verify(d: Path, stem: str, body: str = "CREATE TABLE t (x int);") -> None:
    _write(d, f"{stem}.sql", body)
    _write(d, f"{stem}.verify.sql", "DO $$ BEGIN NULL; END $$;")


# ---------------------------------------------------------------------------
# The transaction-control refusal. This is the guard PharmFoldMDK 3.1 bought.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "body",
    [
        "BEGIN;\nCREATE TABLE t (x int);",
        "CREATE TABLE t (x int);\nCOMMIT;",
        "CREATE TABLE t (x int);\nROLLBACK;",
        "SAVEPOINT s;\nCREATE TABLE t (x int);",
        "START TRANSACTION;\nCREATE TABLE t (x int);",
        "begin;\ncreate table t (x int);",  # case-insensitive
    ],
)
def test_transaction_control_is_refused(body):
    with pytest.raises(migrate.MigrationError, match="transaction control"):
        migrate._reject_transaction_control(body, "test file")


def test_plpgsql_block_is_not_mistaken_for_transaction_control():
    """A DO block's BEGIN/END is not transaction control, and must not trip.

    This is the false-positive direction, and it matters: a guard that refuses
    every verification file we write would be turned off within a day, and a
    guard that is turned off protects nothing.
    """
    body = """
    DO $$
    DECLARE n integer;
    BEGIN
        SELECT 1 INTO n;
        IF n <> 1 THEN
            RAISE EXCEPTION 'nope';
        END IF;
    END $$;
    """
    migrate._reject_transaction_control(body, "test file")  # must not raise


def test_transaction_control_inside_a_comment_is_ignored():
    body = "-- COMMIT; this is prose about committing\nCREATE TABLE t (x int);"
    migrate._reject_transaction_control(body, "test file")  # must not raise


def test_the_real_migration_files_contain_no_transaction_control():
    """The shipped 0001 must satisfy its own runner."""
    for m in migrate.discover():
        migrate._reject_transaction_control(m.sql, m.path.name)
        assert m.verify_path is not None, f"{m.name} has no verification file"
        migrate._reject_transaction_control(m.verify_sql, m.verify_path.name)


# ---------------------------------------------------------------------------
# Discovery, naming and ordering
# ---------------------------------------------------------------------------

def test_discovers_in_version_order(tmp_path):
    _with_verify(tmp_path, "0002_second")
    _with_verify(tmp_path, "0001_first")
    found = migrate.discover(tmp_path)
    assert [m.version for m in found] == [1, 2]
    assert [m.name for m in found] == ["0001_first", "0002_second"]


def test_unparseable_filename_is_refused(tmp_path):
    _write(tmp_path, "not_a_migration.sql")
    with pytest.raises(migrate.MigrationError, match="not a valid migration filename"):
        migrate.discover(tmp_path)


def test_gap_in_sequence_is_refused(tmp_path):
    _with_verify(tmp_path, "0001_first")
    _with_verify(tmp_path, "0003_third")
    with pytest.raises(migrate.MigrationError, match="gap in migration sequence"):
        migrate.discover(tmp_path)


def test_verify_file_is_not_itself_a_migration(tmp_path):
    _with_verify(tmp_path, "0001_first")
    assert [m.version for m in migrate.discover(tmp_path)] == [1]


# ---------------------------------------------------------------------------
# Forward-only, and the checksum
# ---------------------------------------------------------------------------

def test_plan_returns_only_pending(tmp_path):
    _with_verify(tmp_path, "0001_first")
    _with_verify(tmp_path, "0002_second")
    ms = migrate.discover(tmp_path)
    applied = {1: ("0001_first", ms[0].sha256)}
    assert [m.version for m in migrate.plan(ms, applied)] == [2]


def test_migration_below_high_water_mark_is_refused(tmp_path):
    """The rebase / bad-merge case. Forward-only means forward."""
    _with_verify(tmp_path, "0001_first")
    _with_verify(tmp_path, "0002_second")
    ms = migrate.discover(tmp_path)
    applied = {2: ("0002_second", ms[1].sha256)}  # 0001 somehow never recorded
    with pytest.raises(migrate.MigrationError, match="numbered below one already applied"):
        migrate.plan(ms, applied)


def test_changed_file_is_refused(tmp_path):
    """A migration whose file changed is a different migration, same number."""
    _with_verify(tmp_path, "0001_first")
    ms = migrate.discover(tmp_path)
    applied = {1: ("0001_first", "0" * 64)}
    with pytest.raises(migrate.MigrationError, match="has changed since it was applied"):
        migrate.check_integrity(ms, applied)


def test_unchanged_file_passes_integrity(tmp_path):
    _with_verify(tmp_path, "0001_first")
    ms = migrate.discover(tmp_path)
    migrate.check_integrity(ms, {1: ("0001_first", ms[0].sha256)})


def test_placeholder_checksum_is_tolerated(tmp_path):
    """A pre-runner manual application recorded SET-BY-RUNNER; do not block on it."""
    _with_verify(tmp_path, "0001_first")
    ms = migrate.discover(tmp_path)
    migrate.check_integrity(ms, {1: ("0001_first", "SET-BY-RUNNER")})


def test_applied_migration_missing_from_repo_is_refused(tmp_path):
    """The database says it ran; the repository has never heard of it."""
    _with_verify(tmp_path, "0001_first")
    ms = migrate.discover(tmp_path)
    applied = {
        1: ("0001_first", ms[0].sha256),
        2: ("0002_vanished", "a" * 64),
    }
    with pytest.raises(migrate.MigrationError, match="not in the repository"):
        migrate.check_integrity(ms, applied)


def test_checksum_changes_with_content(tmp_path):
    p = _write(tmp_path, "0001_first.sql", "CREATE TABLE a (x int);")
    _write(tmp_path, "0001_first.verify.sql", "DO $$ BEGIN NULL; END $$;")
    before = migrate.discover(tmp_path)[0].sha256
    p.write_text("CREATE TABLE b (x int);", encoding="utf-8")
    assert migrate.discover(tmp_path)[0].sha256 != before


# ---------------------------------------------------------------------------
# The runner refuses to run without a DSN, and never invents one
# ---------------------------------------------------------------------------

def test_no_dsn_is_an_error_not_a_default(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(migrate.MigrationError, match="DATABASE_URL is not set"):
        migrate._connect(None)
