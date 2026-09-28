"""Per-index I/O attributable to one quarter's load. Snapshot, then diff.

    python tools/index_io.py snapshot before.json
    ... let exactly one quarter commit ...
    python tools/index_io.py snapshot after.json
    python tools/index_io.py diff before.json after.json

WHY A BEFORE/AFTER DELTA AND NOT A LIVE READING
-------------------------------------------------
Two things make the obvious approaches wrong here, and both are already in the
register.

**`pg_locks` cannot answer it.** Locks record what a transaction has TOUCHED,
not where its time went. A load holds locks on `fact` and all seven of its
indexes from the moment it starts until it commits, so a live lock listing looks
identical whether an index is costing everything or nothing. Reading a phase out
of a lock listing is the mistake `tools/load_progress.py` made in its first
version.

**Counters do not flush mid-transaction (F-032).** Sampling
`pg_statio_user_indexes` while a quarter is loading reports the state before it
started, and a conclusion was already drawn from exactly that kind of reading
and was wrong.

A delta between two commits has neither problem: both readings are taken outside
a transaction, and everything between them is attributable to the quarter that
committed in between.

WHAT IT ANSWERS
---------------
`idx_blks_read` is index pages fetched **from disk**; `idx_blks_hit` is pages
found in cache. On a 1 GB Basic instance the working set does not fit, so disk
reads are the cost. If the five droppable indexes dominate the read delta,
dropping them for the run is justified. **If `fact_pkey` and
`fact_one_per_filing` dominate, dropping the other five buys little** - and
those two cannot be dropped: one is identity, the other is the `ON CONFLICT`
arbiter without which duplicate facts become representable.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

# Cannot be dropped. fact_pkey is identity; fact_one_per_filing is the
# ON CONFLICT arbiter and the schema's refusal of duplicate facts.
NOT_DROPPABLE = {"fact_pkey", "fact_one_per_filing"}

SQL = """
SELECT s.indexrelname,
       s.idx_blks_read,
       s.idx_blks_hit,
       i.idx_scan,
       pg_relation_size(s.indexrelid) AS bytes
FROM   pg_statio_user_indexes s
JOIN   pg_stat_user_indexes  i USING (indexrelid)
WHERE  s.relname = 'fact'
ORDER  BY 1
"""


def snapshot(dsn: str) -> dict:
    import psycopg
    with psycopg.connect(dsn, autocommit=True, connect_timeout=20) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM coverage_quarter")
            quarters = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM fact")
            facts = cur.fetchone()[0]
            cur.execute(SQL)
            idx = {r[0]: {"read": r[1], "hit": r[2], "scan": r[3], "bytes": r[4]}
                   for r in cur.fetchall()}
    return {"at": datetime.now(timezone.utc).isoformat(),
            "quarters": quarters, "facts": facts, "indexes": idx}


def diff(a: dict, b: dict) -> int:
    dq = b["quarters"] - a["quarters"]
    df = b["facts"] - a["facts"]
    print(f"between snapshots: {dq} quarter(s), {df:,} facts\n")
    if dq != 1:
        print(f"WARNING: {dq} quarters committed, not 1. The delta is not "
              f"attributable to a single quarter.\n", file=sys.stderr)

    rows = []
    for name, after in b["indexes"].items():
        before = a["indexes"].get(name, {"read": 0, "hit": 0, "bytes": 0})
        rows.append((
            name,
            after["read"] - before["read"],
            after["hit"] - before["hit"],
            after["bytes"] - before["bytes"],
        ))

    total_read = sum(r[1] for r in rows) or 1
    drop_read = sum(r[1] for r in rows if r[0] not in NOT_DROPPABLE)

    w = max(len(r[0]) for r in rows)
    print(f"{'index':<{w}}  {'disk reads':>12} {'share':>7}  "
          f"{'cache hits':>12}  {'grew':>10}  droppable")
    for name, read, hit, grew in sorted(rows, key=lambda r: -r[1]):
        print(f"{name:<{w}}  {read:>12,} {100*read/total_read:>6.1f}%  "
              f"{hit:>12,}  {grew/2**20:>8.1f}MB  "
              f"{'no' if name in NOT_DROPPABLE else 'YES'}")

    pct = 100 * drop_read / total_read
    print(f"\ndroppable indexes account for {pct:.1f}% of index disk reads")
    if pct >= 60:
        print("=> Dropping them for the run is justified on this evidence.")
    else:
        print("=> NOT justified. The cost is in indexes that cannot be dropped,\n"
              "   so restructuring --defer-indexes would buy little. Look at the\n"
              "   plan's RAM (OPEN-57) instead.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="index_io")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot")
    s.add_argument("path")
    s.add_argument("--dsn", default=os.environ.get("DATABASE_URL"))
    d = sub.add_parser("diff")
    d.add_argument("before")
    d.add_argument("after")
    args = p.parse_args(argv)

    if args.cmd == "snapshot":
        if not args.dsn:
            print("No DSN.", file=sys.stderr)
            return 2
        snap = snapshot(args.dsn)
        with open(args.path, "w", encoding="utf-8") as fh:
            json.dump(snap, fh, indent=2)
        print(f"{args.path}: {snap['quarters']} quarters, "
              f"{snap['facts']:,} facts, {len(snap['indexes'])} indexes")
        return 0

    with open(args.before, encoding="utf-8") as fh:
        a = json.load(fh)
    with open(args.after, encoding="utf-8") as fh:
        b = json.load(fh)
    return diff(a, b)


if __name__ == "__main__":
    raise SystemExit(main())
