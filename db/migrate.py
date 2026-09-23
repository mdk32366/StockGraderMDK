"""Forward-only SQL migration runner — D-021's implementation.

D-021 requires numbered, forward-only SQL migrations applied by a runner we own,
each in its own transaction, under an advisory lock, followed by a verification
query asserting the objects it claims to create exist and are the right shape.

WHY WE OWN THE TRANSACTION, AND THE FILES DO NOT
------------------------------------------------
D-021 rejected Alembic on the strength of PharmFoldMDK §3.1: a migration chain
that *silently rolled itself back* because a statement ran before the transaction
the tool owned. That is what happens when the file and the tool both believe they
own the transaction — and it fails quietly, which is the worst direction.

So exactly one of them may, and it is this runner. ``_reject_transaction_control``
makes the other case impossible rather than discouraged: a migration or
verification file containing BEGIN/COMMIT/ROLLBACK/SAVEPOINT is refused before a
connection is opened.

WHY A TRANSACTION-SCOPED LOCK
-----------------------------
D-021 says "session advisory lock". This uses ``pg_advisory_xact_lock``, which is
transaction-scoped. The app connects through pgbouncer
(F-next/app-connects-via-pgbouncer), and a session-scoped ``pg_advisory_lock`` is
unreliable under transaction pooling — the session a lock is taken on is not
guaranteed to be the session the next statement runs on. A transaction-scoped
lock covers exactly the unit D-021 already specifies and releases on COMMIT or
ROLLBACK, with no explicit unlock for a crash to skip. Stricter, not looser.

WHAT THIS RUNS AS
-----------------
A ``schema_admin``. A ``writer`` is refused CREATE TABLE by design (A-017,
D-031), which is what keeps schema rights out of the web process. The runner
reads DATABASE_URL from the environment and never writes it anywhere.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"

# Matched at statement position, after comments AND dollar-quoted bodies have
# been stripped (see _strip_sql_comments). The stripping is what makes `END;`
# safe to include: at top level PostgreSQL treats END as a synonym for COMMIT,
# but inside a PL/pgSQL body it is block structure and appears constantly.
# Without the strip this pattern fires on correct files.
_TXN_CONTROL = re.compile(
    r"^\s*(BEGIN\s*;|COMMIT\b|ROLLBACK\b|SAVEPOINT\b|RELEASE\s+SAVEPOINT\b"
    r"|START\s+TRANSACTION\b|END\s*;)",
    re.IGNORECASE | re.MULTILINE,
)

_FILENAME = re.compile(r"^(\d{4})_([a-z0-9_]+)\.sql$")

# One advisory lock for the whole runner, not one per migration. Two runners
# must not apply different migrations concurrently, so the lock protects the
# ledger, not an individual file.
LOCK_KEY = 20260921


class MigrationError(RuntimeError):
    """Anything that should stop the run. Always fatal, never warned about."""


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    path: Path
    verify_path: Path | None

    @property
    def sql(self) -> str:
        return self.path.read_text(encoding="utf-8")

    @property
    def verify_sql(self) -> str | None:
        if self.verify_path is None:
            return None
        return self.verify_path.read_text(encoding="utf-8")

    @property
    def sha256(self) -> str:
        """Checksum of the migration file as it exists now.

        A migration whose file has changed since it was applied is a different
        migration wearing the same number. The ledger stores this so that
        difference is detectable rather than invisible.
        """
        return hashlib.sha256(self.path.read_bytes()).hexdigest()


def _strip_sql_comments(sql: str) -> str:
    """Reduce SQL to top-level statement text.

    Removes -- line comments, /* */ blocks, and **dollar-quoted bodies**. The
    last is the one that matters. A PL/pgSQL block is full of ``BEGIN``, ``END``
    and ``EXCEPTION ... END;`` that are block structure, not transaction
    control. Scanning inside them raises on correct files — and a guard that
    cries wolf on correct files gets switched off, after which it protects
    nothing. This was not hypothetical: it fired on 0001's own verification
    file the first time the guard ran.
    """
    sql = re.sub(r"\$(\w*)\$.*?\$\1\$", " ", sql, flags=re.DOTALL)
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    sql = re.sub(r"--[^\n]*", " ", sql)
    return sql


def _reject_transaction_control(sql: str, what: str) -> None:
    """Refuse a file that tries to own the transaction. See module docstring."""
    hit = _TXN_CONTROL.search(_strip_sql_comments(sql))
    if hit:
        raise MigrationError(
            f"{what} contains transaction control ({hit.group(1).strip()!r}). "
            "The runner owns the transaction; a file that also opens or closes "
            "one is how PharmFoldMDK 3.1 rolled a migration chain back silently. "
            "Remove it."
        )


def discover(directory: Path = MIGRATIONS_DIR) -> list[Migration]:
    """Find migrations, ordered by version, refusing anything ambiguous."""
    if not directory.is_dir():
        raise MigrationError(f"migrations directory not found: {directory}")

    found: dict[int, Migration] = {}
    for path in sorted(directory.glob("*.sql")):
        if path.name.endswith(".verify.sql"):
            continue
        match = _FILENAME.match(path.name)
        if not match:
            raise MigrationError(
                f"{path.name!r} is not a valid migration filename. "
                "Expected NNNN_lower_snake_name.sql — an unparseable name has no "
                "position in a forward-only order."
            )
        version = int(match.group(1))
        if version in found:
            raise MigrationError(
                f"two migrations share version {version}: "
                f"{found[version].path.name} and {path.name}"
            )
        verify = path.with_name(path.name[:-4] + ".verify.sql")
        found[version] = Migration(
            version=version,
            name=path.stem,
            path=path,
            verify_path=verify if verify.exists() else None,
        )

    migrations = [found[v] for v in sorted(found)]

    # Gaps are refused. A missing 0003 means either a migration was deleted or
    # one is unmerged, and both are states where "apply everything pending" is
    # the wrong instruction.
    for expected, m in enumerate(migrations, start=1):
        if m.version != expected:
            raise MigrationError(
                f"gap in migration sequence: expected {expected:04d}, found "
                f"{m.version:04d} ({m.path.name}). Forward-only ordering cannot "
                "be established with a hole in it."
            )
    return migrations


def ensure_ledger(cur) -> None:
    """Create schema_migration if absent.

    The ledger belongs to the runner, not to any migration — 0001 deliberately
    does not create it. A migration that creates the ledger cannot be recorded
    in the ledger until after it has created it, which is a bootstrap knot; and
    a migration that records its own application can record it wrongly. The
    runner writes version, name and the file's real sha256 in the same
    transaction as the DDL, so the record and the change succeed or fail
    together.
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migration (
            version    integer     PRIMARY KEY,
            name       text        NOT NULL,
            applied_at timestamptz NOT NULL DEFAULT now(),
            sha256     text        NOT NULL
        )
        """
    )


def applied_state(cur) -> dict[int, tuple[str, str]]:
    cur.execute("SELECT version, name, sha256 FROM schema_migration ORDER BY version")
    return {row[0]: (row[1], row[2]) for row in cur.fetchall()}


def check_integrity(migrations: list[Migration], applied: dict[int, tuple[str, str]]) -> None:
    """Refuse to proceed if the past has changed underneath us."""
    on_disk = {m.version for m in migrations}
    for version, (name, sha) in sorted(applied.items()):
        if version not in on_disk:
            raise MigrationError(
                f"migration {version:04d} ({name}) is recorded as applied but its "
                "file is not in the repository. The database and the repository "
                "disagree about history."
            )
        m = next(x for x in migrations if x.version == version)
        if sha == "SET-BY-RUNNER":
            continue  # placeholder from a pre-runner manual application
        if m.sha256 != sha:
            raise MigrationError(
                f"migration {version:04d} ({m.name}) has changed since it was "
                f"applied.\n  recorded: {sha}\n  on disk:  {m.sha256}\n"
                "A migration whose file changed is a different migration wearing "
                "the same number. Forward-only means writing 0002, not editing "
                "0001."
            )


def plan(migrations: list[Migration], applied: dict[int, tuple[str, str]]) -> list[Migration]:
    """Pending migrations, in order. Forward-only: nothing below the high-water mark."""
    if not applied:
        return list(migrations)
    high_water = max(applied)
    pending = [m for m in migrations if m.version not in applied]
    behind = [m for m in pending if m.version < high_water]
    if behind:
        raise MigrationError(
            "refusing to apply a migration numbered below one already applied: "
            + ", ".join(f"{m.version:04d} ({m.name})" for m in behind)
            + f"; highest applied is {high_water:04d}. This is what forward-only "
            "means, and it is usually a rebase or a bad merge rather than an "
            "intention."
        )
    return pending


def apply_one(conn, m: Migration, *, verbose: bool = True) -> None:
    """Apply one migration, verify it, and record it — all in one transaction.

    The verification runs inside a SAVEPOINT that is rolled back afterwards, so
    fixtures it inserts vanish while the migration survives. A failed
    verification raises, which takes the whole transaction — including the DDL —
    down with it. "The migration reported success" and "the schema is right" are
    different claims (D-005's shape); this makes the second one load-bearing.
    """
    sql = m.sql
    _reject_transaction_control(sql, f"migration {m.path.name}")
    verify_sql = m.verify_sql
    if verify_sql is not None:
        _reject_transaction_control(verify_sql, f"verification {m.verify_path.name}")

    sha = m.sha256

    with conn.cursor() as cur:
        # Transaction-scoped: released by COMMIT or ROLLBACK, pooler-safe.
        cur.execute("SELECT pg_advisory_xact_lock(%s)", (LOCK_KEY,))
        ensure_ledger(cur)

        if verbose:
            print(f"  applying  {m.version:04d} {m.name}")
        cur.execute(sql)

        if verify_sql is None:
            raise MigrationError(
                f"migration {m.path.name} has no {m.path.stem}.verify.sql. "
                "D-021 requires a verification query; a migration without one "
                "can only report that it ran, not that it worked."
            )

        if verbose:
            print(f"  verifying {m.version:04d}")
        cur.execute("SAVEPOINT verification")
        cur.execute(verify_sql)
        # Undo fixtures; keep the DDL. If the verification raised, we never
        # reach here and the whole transaction unwinds.
        cur.execute("ROLLBACK TO SAVEPOINT verification")
        cur.execute("RELEASE SAVEPOINT verification")

        cur.execute(
            """
            INSERT INTO schema_migration (version, name, sha256)
            VALUES (%s, %s, %s)
            ON CONFLICT (version) DO UPDATE
                SET name = EXCLUDED.name, sha256 = EXCLUDED.sha256
            """,
            (m.version, m.name, sha),
        )
    conn.commit()
    if verbose:
        print(f"  ok        {m.version:04d} {m.name}  sha256={sha[:12]}")


def _connect(dsn: str | None):
    try:
        import psycopg
    except ImportError as exc:  # pragma: no cover - dependency is declared
        raise MigrationError("psycopg is required to run migrations") from exc

    dsn = dsn or os.environ.get("DATABASE_URL")
    if not dsn:
        raise MigrationError(
            "DATABASE_URL is not set. The runner takes the DSN from the "
            "environment and never stores it."
        )
    return psycopg.connect(dsn, autocommit=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="migrate",
        description="Forward-only SQL migration runner (D-021).",
    )
    parser.add_argument(
        "command",
        choices=["status", "plan", "apply"],
        help="status: what is applied. plan: what would run (default, read-only). "
             "apply: actually run it.",
    )
    parser.add_argument("--dsn", default=None, help="override DATABASE_URL")
    parser.add_argument(
        "--dir", default=None, help="migrations directory (default: db/migrations)"
    )
    args = parser.parse_args(argv)

    directory = Path(args.dir) if args.dir else MIGRATIONS_DIR

    try:
        migrations = discover(directory)

        # Scan every file before opening a connection. A file that should never
        # run should be refused before we are anywhere near the database.
        for m in migrations:
            _reject_transaction_control(m.sql, f"migration {m.path.name}")
            if m.verify_path is not None:
                _reject_transaction_control(
                    m.verify_sql, f"verification {m.verify_path.name}"
                )

        conn = _connect(args.dsn)
        try:
            with conn.cursor() as cur:
                ensure_ledger(cur)
            conn.commit()

            with conn.cursor() as cur:
                applied = applied_state(cur)
            check_integrity(migrations, applied)
            pending = plan(migrations, applied)

            if args.command == "status":
                print(f"{len(applied)} applied, {len(pending)} pending")
                for m in migrations:
                    mark = "applied" if m.version in applied else "PENDING"
                    print(f"  {m.version:04d} {m.name:<28} {mark}")
                return 0

            if not pending:
                print("nothing to apply; schema is up to date")
                return 0

            if args.command == "plan":
                print(f"{len(pending)} migration(s) would be applied:")
                for m in pending:
                    verify = m.verify_path.name if m.verify_path else "NO VERIFICATION"
                    print(f"  {m.version:04d} {m.name:<28} verify={verify}")
                print("\nre-run with 'apply' to execute")
                return 0

            for m in pending:
                try:
                    apply_one(conn, m)
                except MigrationError:
                    raise
                except Exception as exc:
                    # A database error during a migration is a report, not a
                    # traceback. The transaction has already unwound - nothing
                    # is half-applied - and what the operator needs is which
                    # migration failed and why, not a Python stack.
                    conn.rollback()
                    raise MigrationError(
                        f"migration {m.version:04d} ({m.name}) failed and was "
                        f"rolled back in full.\n"
                        f"  {type(exc).__name__}: {exc}\n"
                        "Nothing was applied and the ledger was not written."
                    ) from exc
            print(f"applied {len(pending)} migration(s)")
            return 0
        finally:
            conn.close()

    except MigrationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
