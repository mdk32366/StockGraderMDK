"""Is a load actually progressing, or has it stalled? Read-only.

    .venv\\Scripts\\python.exe tools\\load_progress.py

WHY pg_locks AND NOT pg_stat_activity
--------------------------------------
`schema_admin` gets `<insufficient privilege>` from `pg_stat_activity` and
cannot see other sessions at all. `pg_locks` is readable and shows which
relations a transaction has touched. That is how the stalled load was diagnosed
on 2026-09-25 (builder closeout 1.6).

WHY IT DOES NOT REPORT A ROW COUNT
-----------------------------------
`pg_stat_database` counters **do not flush mid-transaction**. `tup_inserted`
reading 0 during a long load means nothing, and a conclusion was already drawn
from exactly that and was wrong (F-032). So this reports locks, which are true
now, rather than counters, which are not.

A long load is one transaction. Until it commits, another session sees no rows
in `fact` no matter how many have been written -- that is correct behaviour and
not evidence of a stall.
"""

from __future__ import annotations

import argparse
import os
import sys

WATCH = ("fact", "filing", "filer", "fact_collision", "coverage_quarter",
         "fetch_log")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="load_progress")
    p.add_argument("--dsn", default=os.environ.get("DATABASE_URL"),
                   help="defaults to DATABASE_URL")
    args = p.parse_args(argv)

    if not args.dsn:
        print("No DSN. Set DATABASE_URL or pass --dsn.", file=sys.stderr)
        return 2

    try:
        import psycopg
    except ImportError as exc:
        print(f"psycopg is required: {exc}", file=sys.stderr)
        return 2

    with psycopg.connect(args.dsn, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.relname, l.mode, l.granted, count(*)
            FROM   pg_locks l
            JOIN   pg_class c ON c.oid = l.relation
            WHERE  l.relation IS NOT NULL
              AND  c.relname = ANY(%s)
            GROUP  BY 1, 2, 3
            ORDER  BY 1, 2
            """,
            (list(WATCH),),
        )
        rows = cur.fetchall()

        # Our own connection holds nothing interesting; anything here belongs
        # to another session, which is the point.
        cur.execute("SELECT count(*) FROM pg_locks WHERE relation IS NOT NULL")
        total = cur.fetchone()[0]

    if not rows:
        print("No locks on the load tables.")
        print("Either the load has not reached its inserts yet, or it has "
              "finished or died. This does NOT distinguish those.")
        print(f"(total relation locks visible: {total})")
        return 1

    width = max(len(r[0]) for r in rows)
    print("Locks held on load tables -- a transaction is touching these now:\n")
    for relname, mode, granted, n in rows:
        state = "granted" if granted else "WAITING"
        print(f"  {relname:<{width}}  {mode:<24} {state}  x{n}")
    print("\nProgressing. Row counts will stay at zero for other sessions "
          "until it commits (F-032) -- that is correct, not a stall.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
