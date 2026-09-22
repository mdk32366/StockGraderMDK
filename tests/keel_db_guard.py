"""KEEL database-safety guard (Principle 5, V10 positive-identity clause).

The test suite is entitled to treat its database as disposable. This guard
makes sure that belief is TRUE before any test runs.

WHAT IT CHECKS — positive identity, never location:
  The hostname and port are NEVER consulted. A tunnel to production is
  localhost; a guard that reads the hostname is defeated by it (the 4,535-row
  scar). If DATABASE_URL is set, BOTH factors are required:

  Factor 1 — a sentence a human has to mean. The environment variable
      KEEL_TEST_DB_DISPOSABLE must equal CONFIRM_SENTENCE exactly. It must be
      typed by hand in the shell that runs the suite and must never appear in
      any env file (tests/test_hygiene.py fails the suite if it does).
  Factor 2 — the database vouches for itself. The table
      keel_disposable_canary must exist. Only db/keel_canary.sql creates it,
      and that script is run by hand against disposable databases only.

  Tripwire (in addition to, not instead of, the factors): no user table may
  hold more than MAX_DISPOSABLE_ROWS rows.

DIRECTION — it fails closed on every unexpected input:
  DATABASE_URL unset             -> HERMETIC mode. No DB in play; any test that
                                    asks for the database ERRORS (never skips).
  DATABASE_URL set but blank     -> hard error (malformed input).
  Factor missing or wrong        -> hard error; the probe is never called.
  Probe fails for any reason     -> hard error (including psycopg not installed).

SCOPE: it protects connections made through the `db_url` fixture in
conftest.py. tests/test_hygiene.py fails if any test opens a connection any
other way, so that scope is enforced, not assumed.

To defeat this guard against production, someone must deliberately run the
canary script against production AND type the confirmation sentence in a shell
pointed at it. That is two separate deliberate acts; no single loaded env file
can do both. Whether that residual is acceptable is owner ruling D-004.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

CONFIRM_ENV = "KEEL_TEST_DB_DISPOSABLE"
CONFIRM_SENTENCE = "I confirm this database is disposable"
CANARY_TABLE = "keel_disposable_canary"
MAX_DISPOSABLE_ROWS = 10_000

HERMETIC = "HERMETIC"
DISPOSABLE_VERIFIED = "DISPOSABLE_VERIFIED"


class UnsafeDatabaseError(RuntimeError):
    """Raised when the suite must not run. Always a hard error, never a skip."""


@dataclass(frozen=True)
class ProbeResult:
    canary_present: bool
    max_table_rows: int


Probe = Callable[[str], ProbeResult]


def check_database_is_disposable(env: Mapping[str, str], probe: Probe) -> str:
    """Return HERMETIC or DISPOSABLE_VERIFIED, or raise UnsafeDatabaseError."""
    url = env.get("DATABASE_URL")
    if url is None:
        return HERMETIC
    if not url.strip():
        raise UnsafeDatabaseError(
            "DATABASE_URL is set but blank. Unset it for hermetic runs, or point "
            "it at a disposable database. Refusing to guess."
        )

    # Factor 1 — checked BEFORE touching the database at all.
    if env.get(CONFIRM_ENV) != CONFIRM_SENTENCE:
        raise UnsafeDatabaseError(
            f"DATABASE_URL is set, but {CONFIRM_ENV} does not equal the "
            f"confirmation sentence. Type it by hand in this shell if — and only "
            f"if — this database is disposable. The hostname is never trusted: "
            f"a tunnel to production is localhost."
        )

    # Factor 2 + tripwire — the database must vouch for itself.
    try:
        result = probe(url)
    except UnsafeDatabaseError:
        raise
    except Exception as exc:  # any probe failure is a refusal, not a pass
        raise UnsafeDatabaseError(
            f"Could not verify database identity ({type(exc).__name__}: {exc}). "
            f"Refusing to run."
        ) from exc

    if not result.canary_present:
        raise UnsafeDatabaseError(
            f"Canary table {CANARY_TABLE} not found. This database has not been "
            f"marked disposable (db/keel_canary.sql). Refusing to run."
        )
    if result.max_table_rows > MAX_DISPOSABLE_ROWS:
        raise UnsafeDatabaseError(
            f"A table holds more than {MAX_DISPOSABLE_ROWS:,} rows "
            f"(found {result.max_table_rows:,}). Disposable databases are small. "
            f"Refusing to run."
        )
    return DISPOSABLE_VERIFIED


def postgres_probe(url: str) -> ProbeResult:
    """Real probe. Exact, bounded counts — pg_stat estimates can read 0 after a
    bulk load, which would make the tripwire pass on a full table."""
    try:
        import psycopg  # noqa: PLC0415 — only needed when a DB is in play
    except ImportError as exc:
        raise UnsafeDatabaseError(
            "DATABASE_URL is set but psycopg is not installed, so identity "
            "cannot be verified. Refusing to run."
        ) from exc

    limit = MAX_DISPOSABLE_ROWS + 1
    with psycopg.connect(url, connect_timeout=5) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
            "WHERE table_name = %s)",
            (CANARY_TABLE,),
        )
        canary = bool(cur.fetchone()[0])
        cur.execute(
            "SELECT quote_ident(schemaname) || '.' || quote_ident(relname) "
            "FROM pg_stat_user_tables"
        )
        tables = [row[0] for row in cur.fetchall()]
        max_rows = 0
        for table in tables:
            cur.execute(f"SELECT count(*) FROM (SELECT 1 FROM {table} LIMIT {limit}) t")
            max_rows = max(max_rows, int(cur.fetchone()[0]))
    return ProbeResult(canary_present=canary, max_table_rows=max_rows)


def require_verified(mode: str) -> None:
    """Called by the db_url fixture. HERMETIC mode + a DB-requesting test is an
    ERROR, never a skip: a skip is how a dangerous thing comes to look harmless."""
    if mode != DISPOSABLE_VERIFIED:
        raise UnsafeDatabaseError(
            "This test needs a database, but none was verified disposable. "
            "Set DATABASE_URL to a disposable database and confirm it."
        )
