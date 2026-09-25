"""Load the ruled window, quarter by quarter. Restartable by re-running.

    .venv\\Scripts\\python.exe tools\\load_window.py --cache D:\\fsds --dry-run
    .venv\\Scripts\\python.exe tools\\load_window.py --cache D:\\fsds --go

WHY THE DATABASE IS THE STATE AND THIS SCRIPT HAS NONE
--------------------------------------------------------
`coverage_quarter.quarter` is a primary key and the loader writes one row per
quarter. So *what has been loaded* is a question with an authoritative answer,
and this driver asks it rather than keeping a progress file that can disagree
with reality. **A progress file is a second source of truth, and the register
already has a finding about relying on a source for the question it cannot
answer.**

That is what makes restart free rather than merely possible (F-034): after any
interruption, re-running skips what is done and resumes at the first gap. A
completed quarter re-run is also a no-op that is *faster* - 63 s against 148 s,
because every row conflicts away rather than inserting - so even a redundant
re-run is cheap and its speed is itself the evidence.

WHY IT STOPS AFTER CONSECUTIVE FAILURES
-----------------------------------------
This runs unattended for many hours. One bad archive should not end the run.
But forty bad archives are one problem repeated, and grinding through them
wastes the night and buries the cause. It stops after `--max-consecutive-
failures`, which defaults to 3, and says which quarter broke first.

IT DOES NOT FETCH
-----------------
Fetching is `tools/fetch_fsds.py`. Separating them means a network failure and
a database failure cannot be confused, and the fetch can finish while the
cluster is untouched.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from ingest.window import quarters  # noqa: E402

PYTHON = REPO / ".venv" / "Scripts" / "python.exe"
LOADER = REPO / "tools" / "load_quarter.py"


def already_loaded(dsn: str) -> set[str]:
    import psycopg
    with psycopg.connect(dsn, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("SELECT quarter FROM coverage_quarter")
        return {r[0] for r in cur.fetchall()}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="load_window")
    p.add_argument("--cache", type=Path, required=True)
    p.add_argument("--dsn", default=os.environ.get("DATABASE_URL"))
    p.add_argument("--first", default=None)
    p.add_argument("--last", default=None)
    p.add_argument("--defer-indexes", action="store_true",
                   help="drop fact's QUERY indexes for the load and rebuild "
                        "after. Built and tested; unused until now.")
    p.add_argument("--max-consecutive-failures", type=int, default=3)
    p.add_argument("--go", action="store_true",
                   help="required. Without it this is a dry run.")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)

    if not args.dsn:
        print("No DSN. Set DATABASE_URL or pass --dsn.", file=sys.stderr)
        return 2

    window = quarters(*(x for x in (args.first, args.last) if x)) \
        if (args.first or args.last) else quarters()

    try:
        done = already_loaded(args.dsn)
    except Exception as exc:                                   # noqa: BLE001
        print(f"Could not read coverage_quarter: {exc}", file=sys.stderr)
        return 2

    missing_archive = [q for q in window
                       if not (args.cache / f"{q}.zip").exists()]
    todo = [q for q in window
            if q not in done and (args.cache / f"{q}.zip").exists()]

    print(f"window          : {window[0]}..{window[-1]}  ({len(window)})")
    print(f"already loaded  : {len(done & set(window))}")
    print(f"archive missing : {len(missing_archive)}")
    print(f"to load         : {len(todo)}\n")

    if missing_archive:
        print("Run tools/fetch_fsds.py first - these have no local archive:")
        print("  " + ", ".join(missing_archive[:12])
              + (f" ... +{len(missing_archive) - 12}" if len(missing_archive) > 12 else ""))
        print()

    if not todo:
        print("Nothing to load.")
        return 0

    if args.dry_run or not args.go:
        for q in todo[:10]:
            print(f"  would load {q}")
        if len(todo) > 10:
            print(f"  ... and {len(todo) - 10} more")
        print("\nNothing was loaded. Pass --go to run.")
        return 0

    started = time.monotonic()
    ok = failed = 0
    consecutive = 0
    first_failure: str | None = None

    for i, q in enumerate(todo, 1):
        stamp = datetime.now(timezone.utc).strftime("%H:%M:%SZ")
        elapsed = time.monotonic() - started
        rate = elapsed / max(ok, 1)
        eta = rate * (len(todo) - i + 1) / 3600
        print(f"\n=== [{i}/{len(todo)}] {q}  {stamp}  "
              f"elapsed {elapsed / 3600:.1f}h  eta ~{eta:.1f}h ===",
              flush=True)

        cmd = [str(PYTHON), str(LOADER), "--quarter", q,
               "--archive", str(args.cache / f"{q}.zip"), "--submissions"]
        if args.defer_indexes:
            cmd.append("--defer-indexes")

        r = subprocess.run(cmd, cwd=REPO)
        if r.returncode == 0:
            ok += 1
            consecutive = 0
        else:
            failed += 1
            consecutive += 1
            first_failure = first_failure or q
            print(f"  FAILED {q} (exit {r.returncode})", file=sys.stderr)
            if consecutive >= args.max_consecutive_failures:
                print(f"\nSTOPPING: {consecutive} consecutive failures. "
                      f"First failure was {first_failure}. "
                      f"Forty bad archives are one problem repeated, and "
                      f"grinding through them buries the cause.",
                      file=sys.stderr)
                break

    total = (time.monotonic() - started) / 3600
    print(f"\nloaded={ok} failed={failed} in {total:.1f}h")
    if first_failure:
        print(f"first failure: {first_failure}. Re-running skips what "
              f"succeeded.", file=sys.stderr)
        return 1
    print("Re-run to verify: a completed quarter is a no-op and is faster, "
          "which is itself the evidence (F-034).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
