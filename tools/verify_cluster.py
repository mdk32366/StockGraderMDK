"""Assert a cluster's state against stated expectations. Exit 1 on any mismatch.

    .venv\\Scripts\\python.exe tools\\verify_cluster.py --dsn "host=... dbname=..." \\
        --expect-facts 3368813 --expect-quarters 1

WHY A TOOL AND NOT TWO SELECTs
-------------------------------
Two SELECTs print numbers. A number printed next to no prior expectation is,
in this register's words, *a count with no prior expectation returns a number
that looks like an answer and nothing disputes it* - and this project has
already recorded twice that the stated expectation caught the counting METHOD
rather than the figures.

So the expectations are arguments, they are compared, and a mismatch is a
non-zero exit rather than a line somebody reads past at the end of a long
session.

Defaults are r1's measured state (2026q2 only), so running it bare after a
migration to a new cluster asks the right question by default.
"""

from __future__ import annotations

import argparse
import sys

# r1, measured. docs/reports/2026-09-25-first-real-load.md and F-034.
R1 = {
    "facts": 3_368_813,
    "quarantined": 195,
    "filings": 7_714,
    "filers": 6_179,
    "quarters": 1,
    "gaps": 0,
    "earliest": "2026q2",
    "latest": "2026q2",
}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="verify_cluster")
    p.add_argument("--dsn", required=True)
    p.add_argument("--expect-facts", type=int, default=R1["facts"])
    p.add_argument("--expect-quarantined", type=int, default=R1["quarantined"])
    p.add_argument("--expect-filings", type=int, default=R1["filings"])
    p.add_argument("--expect-filers", type=int, default=R1["filers"])
    p.add_argument("--expect-quarters", type=int, default=R1["quarters"])
    p.add_argument("--expect-gaps", type=int, default=R1["gaps"])
    p.add_argument("--expect-earliest", default=R1["earliest"])
    p.add_argument("--expect-latest", default=R1["latest"])
    args = p.parse_args(argv)

    try:
        import psycopg
    except ImportError as exc:
        print(f"psycopg is required: {exc}", file=sys.stderr)
        return 2

    checks: list[tuple[str, object, object]] = []

    with psycopg.connect(args.dsn, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("SELECT current_database(), current_user")
        dbname, user = cur.fetchone()
        print(f"database : {dbname}")
        print(f"user     : {user}\n")

        cur.execute("SELECT count(*) FROM fact")
        checks.append(("facts", cur.fetchone()[0], args.expect_facts))

        cur.execute("SELECT count(*) FROM fact_collision")
        checks.append(("quarantined", cur.fetchone()[0], args.expect_quarantined))

        cur.execute("SELECT count(*) FROM filing")
        checks.append(("filings", cur.fetchone()[0], args.expect_filings))

        cur.execute("SELECT count(*) FROM filer")
        checks.append(("filers", cur.fetchone()[0], args.expect_filers))

        cur.execute("SELECT earliest_quarter, latest_quarter, quarters_loaded, "
                    "gaps FROM coverage_window")
        row = cur.fetchone()
        if row is None:
            print("coverage_window returned NO ROW", file=sys.stderr)
            return 1
        earliest, latest, quarters, gaps = row
        checks.append(("earliest", earliest, args.expect_earliest))
        checks.append(("latest", latest, args.expect_latest))
        checks.append(("quarters", quarters, args.expect_quarters))
        checks.append(("gaps", gaps, args.expect_gaps))

        # The migration ledger, because a schema that matches by accident and a
        # schema that was built by the runner are different claims.
        cur.execute("SELECT count(*) FROM schema_migration")
        applied = cur.fetchone()[0]
        checks.append(("migrations_applied", applied, 4))

    width = max(len(n) for n, _, _ in checks)
    failures = 0
    for name, got, want in checks:
        ok = got == want
        failures += not ok
        mark = "ok  " if ok else "FAIL"
        got_s = f"{got:,}" if isinstance(got, int) else str(got)
        want_s = f"{want:,}" if isinstance(want, int) else str(want)
        suffix = "" if ok else f"   expected {want_s}"
        print(f"  {mark} {name:<{width}} {got_s}{suffix}")

    if failures:
        print(f"\n{failures} MISMATCH(ES). This cluster does not reproduce the "
              f"expected state.", file=sys.stderr)
        return 1
    print(f"\nall {len(checks)} checks match.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
