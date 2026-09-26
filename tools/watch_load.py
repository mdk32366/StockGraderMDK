"""Watch a running window load and exit loudly when it stops making progress.

    .venv\\Scripts\\python.exe tools\\watch_load.py --expect 12

WHAT THIS GUARDS, AND WHY IT IS NOT REDUNDANT
-----------------------------------------------
`load_window.py` already stops after consecutive failures, and a crashed run
exits with a code somebody sees. **Neither covers a hang.** A load that stalls -
a dropped proxy mid-COPY, a lock wait that never resolves, a network black hole -
produces no error, no exit, and no output. It looks exactly like a load that is
working, indefinitely.

That is this project's first failure shape almost verbatim: *a check that cannot
run reports the same thing as a system with no defects.* A watcher that only
reports failures it is told about does not cover the case where nothing is told
to anybody.

HOW STALL IS DEFINED, AND WHY IT IS NOT "NO NEW QUARTER"
----------------------------------------------------------
A quarter takes many minutes and commits once at the end, so `quarters_loaded`
sits still for long stretches during healthy work. Using it alone would cry wolf
constantly.

Progress is therefore **either** a new committed quarter **or** the database
growing on disk. A load inside a transaction still allocates pages, so
`pg_database_size` moves while `coverage_quarter` does not. **Both flat for the
stall window means nothing is happening at all** - which is the only claim worth
waking somebody for.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime, timezone


def snapshot(dsn: str) -> tuple[int, int]:
    import psycopg
    with psycopg.connect(dsn, autocommit=True, connect_timeout=20) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM coverage_quarter")
            quarters = cur.fetchone()[0]
            cur.execute("SELECT pg_database_size(current_database())")
            size = cur.fetchone()[0]
    return quarters, size


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="watch_load")
    p.add_argument("--dsn", default=os.environ.get("DATABASE_URL"))
    p.add_argument("--expect", type=int, required=True,
                   help="quarters expected in coverage_quarter when done")
    p.add_argument("--poll-seconds", type=int, default=120)
    p.add_argument("--stall-minutes", type=int, default=20,
                   help="no new quarter AND no database growth for this long")
    p.add_argument("--max-hours", type=float, default=48.0)
    args = p.parse_args(argv)

    if not args.dsn:
        print("No DSN.", file=sys.stderr)
        return 2

    started = time.monotonic()
    last_change = time.monotonic()
    try:
        prev = snapshot(args.dsn)
    except Exception as exc:                                   # noqa: BLE001
        print(f"WATCHDOG: cannot reach the database at all: {exc}",
              file=sys.stderr)
        return 2

    print(f"watching: expect {args.expect} quarters, poll {args.poll_seconds}s, "
          f"stall {args.stall_minutes}m", flush=True)
    print(f"  start: quarters={prev[0]} size={prev[1] / 2**30:.1f} GiB",
          flush=True)

    consecutive_unreachable = 0

    while True:
        time.sleep(args.poll_seconds)
        now = datetime.now(timezone.utc).strftime("%H:%M:%SZ")

        try:
            cur = snapshot(args.dsn)
            consecutive_unreachable = 0
        except Exception as exc:                               # noqa: BLE001
            # A dropped proxy looks like this. Two in a row is a real problem;
            # one may be a blip, and crying wolf teaches people to ignore it.
            consecutive_unreachable += 1
            print(f"  {now} UNREACHABLE ({consecutive_unreachable}): {exc}",
                  file=sys.stderr, flush=True)
            if consecutive_unreachable >= 2:
                print("\nWATCHDOG: database unreachable twice running. The "
                      "proxy has probably dropped. The load cannot be making "
                      "progress.", file=sys.stderr)
                return 1
            continue

        if cur != prev:
            last_change = time.monotonic()
            grew = (cur[1] - prev[1]) / 2**30
            print(f"  {now} quarters={cur[0]} size={cur[1] / 2**30:.1f} GiB "
                  f"({grew:+.2f} GiB)", flush=True)
            prev = cur

        if cur[0] >= args.expect:
            print(f"\nWATCHDOG: reached {cur[0]} quarters, "
                  f"{cur[1] / 2**30:.1f} GiB. Done.", flush=True)
            return 0

        idle_min = (time.monotonic() - last_change) / 60
        if idle_min >= args.stall_minutes:
            print(f"\nWATCHDOG: STALLED. No new quarter and no database growth "
                  f"for {idle_min:.0f} minutes. quarters={cur[0]} of "
                  f"{args.expect}. Nothing is happening - this is the failure "
                  f"that produces no error.", file=sys.stderr)
            return 1

        if (time.monotonic() - started) / 3600 >= args.max_hours:
            print(f"\nWATCHDOG: {args.max_hours}h elapsed, still at "
                  f"{cur[0]}/{args.expect}. Giving up watching, not stopping "
                  f"the load.", file=sys.stderr)
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
