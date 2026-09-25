"""Mark a database disposable, with the target verified rather than trusted.

    .venv\\Scripts\\python.exe tools\\apply_canary.py --dsn "host=... dbname=..." \\
        --expect-database stockgrader_scratch --i-understand-this-marks-it-disposable

WHY THIS EXISTS WHEN db/keel_canary.sql SAYS "NEVER AUTOMATE IT"
----------------------------------------------------------------
That instruction is against the canary running unattended or inside a pipeline,
because marking a database disposable must be a deliberate human act. This does
not automate the decision: it cannot run without an explicit target name and an
explicit acknowledgement flag, neither of which has a default.

What it automates is the part the phase-0 handover says a human does badly:

    "Before you execute it: echo the database name you are actually connected
     to and assert it is stockgrader_scratch. Running the canary against
     stockgrader is one of the two deliberate acts that would defeat the guard,
     and A PROXY CONNECTED TO THE WRONG DATABASE LOOKS EXACTLY LIKE A PROXY
     CONNECTED TO THE RIGHT ONE."

An instruction to eyeball a value is a check that fails silently when somebody
is tired. This refuses on mismatch, before writing anything, in the same
transaction it would write in.

IT REFUSES 'stockgrader' BY NAME
---------------------------------
Belt and braces over the --expect-database comparison. The register's OPEN-1
proof rests on `stockgrader` and `stockgrader_scratch` being indistinguishable
except for this table -- so the one database this must never touch is named
here explicitly, and no flag overrides it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CANARY = REPO / "db" / "keel_canary.sql"

# Never marked disposable, whatever is passed. See OPEN-1.
FORBIDDEN = {"stockgrader", "fly-db", "postgres"}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="apply_canary")
    p.add_argument("--dsn", required=True,
                   help="keyword-form DSN. Password comes from PGPASSWORD, "
                        "never from here.")
    p.add_argument("--expect-database", required=True,
                   help="the database you believe you are connected to")
    p.add_argument("--marked-by", default="owner-at-the-keyboard")
    p.add_argument("--note", default="r2 migration, D-039")
    p.add_argument("--i-understand-this-marks-it-disposable",
                   action="store_true", dest="ack",
                   help="required. The test suite may TRUNCATE a marked "
                        "database.")
    args = p.parse_args(argv)

    if args.expect_database in FORBIDDEN:
        print(f"REFUSED: {args.expect_database!r} is on the never-mark list "
              f"{sorted(FORBIDDEN)}. No flag overrides this.", file=sys.stderr)
        return 2

    if not args.ack:
        print("REFUSED: --i-understand-this-marks-it-disposable is required.",
              file=sys.stderr)
        return 2

    try:
        import psycopg
    except ImportError as exc:
        print(f"psycopg is required: {exc}", file=sys.stderr)
        return 2

    sql = CANARY.read_text(encoding="utf-8")

    with psycopg.connect(args.dsn, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user, version()")
            dbname, user, version = cur.fetchone()

            print(f"connected database : {dbname}")
            print(f"connected user     : {user}")
            print(f"server             : {version.split(',')[0]}")

            # The assertion, before any write, inside the transaction that
            # would do the writing.
            if dbname != args.expect_database:
                conn.rollback()
                print(f"\nREFUSED: connected to {dbname!r}, expected "
                      f"{args.expect_database!r}. Nothing was written.",
                      file=sys.stderr)
                return 1
            if dbname in FORBIDDEN:
                conn.rollback()
                print(f"\nREFUSED: connected to {dbname!r}, which is on the "
                      f"never-mark list. Nothing was written.", file=sys.stderr)
                return 1

            cur.execute(sql)
            cur.execute(
                "INSERT INTO keel_disposable_canary (marked_by, note) "
                "VALUES (%s, %s)", (args.marked_by, args.note))
            conn.commit()

            # Confirm the rows are present afterwards -- the handover asks for
            # this explicitly, and "the statement ran" is not "the row is
            # there".
            cur.execute("SELECT count(*), max(marked_at) "
                        "FROM keel_disposable_canary")
            n, latest = cur.fetchone()

    print(f"\ncanary rows in {dbname}: {n}, latest {latest}")
    if not n:
        print("REFUSED: committed but the table is empty.", file=sys.stderr)
        return 1
    print(f"{dbname} is now marked disposable. The test suite may truncate it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
