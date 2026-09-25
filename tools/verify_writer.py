"""Prove a `writer` account is what D-031 requires. Writes nothing that persists.

    .venv\\Scripts\\python.exe tools\\verify_writer.py --dsn "host=... user=stockgrader_app dbname=stockgrader_scratch"

WHY THIS EXISTS
---------------
*Created-and-given-a-password* is an account that LOOKS usable.
*Connected-and-ran-the-statements* is a usable account. The gap between those
two claims is where D-029's recovery row sat at `Never`, and the register is
explicit that the proof step was not ceremony.

This is A-017's test, made repeatable:

  - it CAN do what the application needs: SELECT, INSERT, UPDATE, DELETE
  - it CANNOT do what the application must not: CREATE TABLE

**The refusal is the evidence**, so exact error text is printed rather than
summarised -- the wording tells you whether the ceiling is the role or
something else.

EVERY PROBE IS SAVEPOINTED, AND THAT IS NOT A DETAIL
-----------------------------------------------------
Postgres aborts the whole transaction on any statement error: every later
statement then fails with `current transaction is aborted`, regardless of
privilege. The first version of this tool savepointed only the DDL probe, so a
single early failure poisoned every check after it and the output said nothing
about WHICH check failed -- a harness reporting a cascade instead of a cause.
Each probe now runs between SAVEPOINT and ROLLBACK TO SAVEPOINT, so the results
are independent and a failure is attributable.

Nothing persists: the outer transaction is rolled back regardless.
"""

from __future__ import annotations

import argparse
import sys

def probe(cur, label: str, sql: str, *, expect_failure: bool = False,
          fetch: bool = False):
    """Run one statement in isolation. Returns (label, ok, detail)."""
    cur.execute("SAVEPOINT p")
    try:
        cur.execute(sql)
        detail = f"{cur.fetchone()[0]:,} rows" if fetch else "ok"
        cur.execute("RELEASE SAVEPOINT p")
        if expect_failure:
            return (label, False, "SUCCEEDED - this account has schema rights")
        return (label, True, detail)
    except Exception as exc:                               # noqa: BLE001
        cur.execute("ROLLBACK TO SAVEPOINT p")
        first = str(exc).strip().splitlines()[0]
        return (label, bool(expect_failure), first)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="verify_writer")
    p.add_argument("--dsn", required=True)
    p.add_argument("--expect-user", default="stockgrader_app")
    args = p.parse_args(argv)

    try:
        import psycopg
    except ImportError as exc:
        print(f"psycopg is required: {exc}", file=sys.stderr)
        return 2

    results = []

    with psycopg.connect(args.dsn, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user")
            dbname, user = cur.fetchone()
            print(f"database : {dbname}")
            print(f"user     : {user}\n")

            if user != args.expect_user:
                print(f"REFUSED: connected as {user!r}, expected "
                      f"{args.expect_user!r}.", file=sys.stderr)
                return 1

            # --- what the app NEEDS -------------------------------------
            results.append(probe(cur, "SELECT on fact",
                                 "SELECT count(*) FROM fact", fetch=True))
            results.append(probe(cur, "SELECT on filing",
                                 "SELECT count(*) FROM filing", fetch=True))

            # Writes go to keel_disposable_canary: a REAL table, in a
            # database explicitly marked disposable, inside a transaction that
            # is rolled back. The first version used a temp table to avoid
            # touching anything real -- but a `writer` has no TEMP privilege
            # here, so the probe table never existed and three write checks
            # cascaded off a missing table rather than testing a privilege.
            # A real table is also the better test: it proves the grant on the
            # kind of object the application actually writes to.
            results.append(probe(cur, "INSERT",
                                 "INSERT INTO keel_disposable_canary "
                                 "(marked_by, note) VALUES "
                                 "('verify_writer', 'probe, rolled back')"))
            results.append(probe(cur, "UPDATE",
                                 "UPDATE keel_disposable_canary SET note = 'p' "
                                 "WHERE marked_by = 'verify_writer'"))
            results.append(probe(cur, "DELETE",
                                 "DELETE FROM keel_disposable_canary "
                                 "WHERE marked_by = 'verify_writer'"))

            # --- what the app MUST NOT ----------------------------------
            results.append(probe(cur, "CREATE TABLE refused",
                                 "CREATE TABLE _writer_should_not_create (x int)",
                                 expect_failure=True))

        conn.rollback()
        print("(rolled back - nothing persisted)\n")

    width = max(len(r[0]) for r in results)
    failures = sum(not ok for _, ok, _ in results)
    for name, ok, detail in results:
        print(f"  {'ok  ' if ok else 'FAIL'} {name:<{width}}  {detail}")

    if failures:
        print(f"\n{failures} check(s) failed. If SELECT failed, the tables were "
              f"created by another role and this account has no GRANT on them - "
              f"that is a missing grant, not a broken role.", file=sys.stderr)
        return 1
    print("\nA-017 holds: this account can do what the app needs and cannot "
          "do what it must not.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
