"""Fetch the window's FSDS archives to a durable cache. Resumable, skippable.

    .venv\\Scripts\\python.exe tools\\fetch_fsds.py --cache D:\\fsds --dry-run
    .venv\\Scripts\\python.exe tools\\fetch_fsds.py --cache D:\\fsds

WHY THIS EXISTS
---------------
`tools/load_quarter.py` takes `--archive`, a LOCAL path. It does not fetch; it
builds the SEC URL only to record provenance. So *"the 45-quarter load is built,
~34 h, restart is free"* is true about the loading and silent about the
fetching: 43 of the 45 archives do not exist on this machine, and they are
~4.24 GB in total.

Everything goes through `EdgarClient`, never a bare HTTP call: D-023's declared
User-Agent, its rate limit, and its rule that a 403 is never retried because a
retry that swallows a refusal turns a policy failure into a silent data gap.

RESUMABILITY IS THE DESIGN, NOT A FEATURE
-------------------------------------------
4.24 GB over a rate-limited client will be interrupted. A quarter already in the
cache, non-empty and openable as a zip, is skipped. So the recovery procedure
for any failure is *run it again*, and the cost of an interruption is the one
archive in flight.

A TRUNCATED DOWNLOAD IS THE FAILURE THIS GUARDS
-------------------------------------------------
A short file is still a file, and a loader pointed at one reports a small
quarter rather than an error - a silent data gap wearing a success. Each archive
is written to a `.part` file and renamed only after it opens as a zip and
contains the two members the loader needs. **A partial download can therefore
never be mistaken for a complete one**, because it never gets the final name.
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from ingest.edgar import EdgarClient, EdgarRefused, EdgarUnavailable  # noqa: E402
from ingest.window import quarters, url  # noqa: E402

# What every FSDS archive must contain for the loader to work. sub.txt is the
# submissions table, num.txt the numeric facts.
REQUIRED_MEMBERS = ("sub.txt", "num.txt")


def is_complete(path: Path) -> bool:
    """A cached archive is usable, not merely present."""
    if not path.exists() or path.stat().st_size == 0:
        return False
    try:
        with zipfile.ZipFile(path) as z:
            names = set(z.namelist())
            return all(m in names for m in REQUIRED_MEMBERS)
    except zipfile.BadZipFile:
        return False


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="fetch_fsds")
    p.add_argument("--cache", type=Path, required=True,
                   help="durable directory. NOT a session scratchpad - the two "
                        "archives that already exist survived by luck.")
    p.add_argument("--first", default=None)
    p.add_argument("--last", default=None)
    p.add_argument("--dry-run", action="store_true",
                   help="report what would be fetched, touch nothing")
    p.add_argument("--seed-from", type=Path, default=None,
                   help="copy any already-cached archives from here first")
    args = p.parse_args(argv)

    window = quarters(*(x for x in (args.first, args.last) if x)) \
        if (args.first or args.last) else quarters()

    if not args.dry_run:
        args.cache.mkdir(parents=True, exist_ok=True)

    # --dry-run must touch nothing, and seeding is a write. Under --dry-run the
    # seed source is only INSPECTED, so the report still reflects what a real
    # run would start from.
    seedable: set[str] = set()
    if args.seed_from and args.seed_from.is_dir():
        for q in window:
            src, dst = args.seed_from / f"{q}.zip", args.cache / f"{q}.zip"
            if src.exists() and not dst.exists() and is_complete(src):
                if args.dry_run:
                    seedable.add(q)
                    print(f"  would seed {q} from {src}")
                else:
                    dst.write_bytes(src.read_bytes())
                    print(f"  seeded {q} from {src}")

    have = [q for q in window
            if q in seedable or is_complete(args.cache / f"{q}.zip")]
    need = [q for q in window if q not in set(have)]

    print(f"window : {window[0]}..{window[-1]}  ({len(window)} quarters)")
    print(f"cached : {len(have)}")
    print(f"to get : {len(need)}\n")

    if not need:
        print("Nothing to fetch. Every archive in the window is cached.")
        return 0

    if args.dry_run:
        for q in need[:8]:
            print(f"  would GET {url(q)}")
        if len(need) > 8:
            print(f"  ... and {len(need) - 8} more")
        print("\n--dry-run: nothing fetched.")
        return 0

    client = EdgarClient()
    got = failed = 0
    total_bytes = 0

    for i, q in enumerate(need, 1):
        dest = args.cache / f"{q}.zip"
        part = dest.with_suffix(".zip.part")
        try:
            f = client.fetch(url(q))
        except EdgarRefused as exc:
            # Never retried. A 403 means the request was refused, and retrying
            # makes it worse while hiding the reason.
            print(f"  [{i}/{len(need)}] REFUSED {q}: {exc}", file=sys.stderr)
            failed += 1
            continue
        except EdgarUnavailable as exc:
            print(f"  [{i}/{len(need)}] UNAVAILABLE {q}: {exc}", file=sys.stderr)
            failed += 1
            continue

        part.write_bytes(f.body)
        if not is_complete(part):
            # Renaming would make a truncated file indistinguishable from a
            # good one at load time. It keeps the .part name and is retried on
            # the next run.
            print(f"  [{i}/{len(need)}] INCOMPLETE {q}: "
                  f"{len(f.body):,} bytes, not a usable archive. Left as .part.",
                  file=sys.stderr)
            failed += 1
            continue

        part.replace(dest)
        got += 1
        total_bytes += len(f.body)
        print(f"  [{i}/{len(need)}] {q}  {len(f.body):,} bytes  "
              f"sha256={f.sha256[:12]}", flush=True)

    print(f"\nfetched={got} failed={failed} bytes={total_bytes:,} "
          f"cache={args.cache}")
    if failed:
        print("Re-run to retry the failures; completed archives are skipped.",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
