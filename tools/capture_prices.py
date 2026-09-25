"""Daily as-traded price capture runner — D-036.

    .venv\\Scripts\\python.exe tools\\capture_prices.py --symbols AAPL,MSFT --dry-run
    .venv\\Scripts\\python.exe tools\\capture_prices.py --symbol-file universe.txt --live

WHY --live IS REQUIRED AND THERE IS NO DEFAULT
-----------------------------------------------
This is the first code in the project that talks to a provider that is not
EDGAR, and OPEN-9 is still open. D-036 is explicit that the provider is
provisional and selects no vendor of record. So a live fetch is opt-in, the
default is a dry run that prints exactly what it would request, and nothing
reaches the network until somebody types --live.

WHAT IT DOES NOT DO
--------------------
It does not touch the database. There is no price schema yet, and D-036 records
that capture to disk may begin before the schema lands because *the dates are
the perishable part, not the loading*. Output is files, shaped so the eventual
migration loads them without renaming a column.

It also does not resolve the migration-numbering collision: the runner refuses
gaps in the sequence (``db/migrate.py`` discover()), 0005 is reserved for
OPEN-64's nil assertions, and a price migration therefore cannot be 0006 until
0005 exists. That is a register question, not a capture question, and capture
does not wait on it.
"""

from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ingest.prices import (  # noqa: E402
    AdjustedOnly,
    PriceParseError,
    PriceRefused,
    RawCapture,
    StooqProvider,
    write_capture,
)

# Deliberately below anything a public endpoint is likely to police. The same
# argument as ingest/edgar.py: sitting on a limit means any burst crosses it,
# and being throttled is a data gap that arrives looking like a success.
REQUESTS_PER_SECOND = 2.0
USER_AGENT = "StockGraderMDK mdk32366@gmail.com"


def fetch(url: str, *, opener=urllib.request.urlopen) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with opener(req, timeout=30) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        # Same rule as D-023: a refusal is not retried blind. Retrying a 403
        # makes it worse and turns a policy failure into a silent data gap.
        raise PriceRefused(f"{url}: HTTP {exc.code}") from exc


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="capture_prices")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--symbols", help="comma-separated, e.g. AAPL,MSFT")
    src.add_argument("--symbol-file", type=Path, help="one symbol per line")
    p.add_argument("--out", type=Path, default=Path("price_capture"),
                   help="output directory (default: ./price_capture)")
    p.add_argument("--live", action="store_true",
                   help="actually fetch. Without it, nothing hits the network.")
    p.add_argument("--dry-run", action="store_true",
                   help="print the URLs that would be fetched, then stop")
    args = p.parse_args(argv)

    if args.symbols:
        symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    else:
        symbols = [ln.strip() for ln in
                   args.symbol_file.read_text(encoding="utf-8").splitlines()
                   if ln.strip() and not ln.startswith("#")]

    if not symbols:
        print("no symbols", file=sys.stderr)
        return 2

    provider = StooqProvider()
    today = datetime.now(timezone.utc).date()

    if args.dry_run or not args.live:
        print(f"DRY RUN - {len(symbols)} symbol(s), provider={provider.name}, "
              f"capture date {today.isoformat()}")
        for s in symbols[:10]:
            print(f"  would GET {provider.daily_url(s)}")
        if len(symbols) > 10:
            print(f"  ... and {len(symbols) - 10} more")
        print("\nNothing was fetched and nothing was written. Pass --live to "
              "capture.")
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    interval = 1.0 / REQUESTS_PER_SECOND
    captured = refused = 0
    same_day = 0

    for i, symbol in enumerate(symbols):
        if i:
            time.sleep(interval)
        url = provider.daily_url(symbol)
        try:
            payload = fetch(url)
            cap = RawCapture.of(url, payload, provider.name)
            bars = provider.parse(symbol, payload, captured_on=today)
        except (PriceRefused, PriceParseError, AdjustedOnly) as exc:
            # Counted and named, never swallowed. A capture that quietly
            # skipped a symbol is a gap shaped like a holiday.
            refused += 1
            print(f"  REFUSED {symbol}: {exc}", file=sys.stderr)
            continue

        write_capture(args.out, cap, bars)
        captured += 1
        same_day += sum(1 for b in bars if b.captured_same_day)

    print(f"\ncaptured={captured} refused={refused} "
          f"bars_with_same_day_guarantee={same_day} out={args.out}")

    # The count that matters is same_day, not captured. A run that wrote files
    # but carried no same-day bar has not advanced the point-in-time series,
    # and the difference is invisible in a file count.
    if captured and same_day == 0:
        print("WARNING: no bar carried the as-traded guarantee. Either the "
              "market was closed, or the provider is serving stale data, and "
              "those are not the same thing.", file=sys.stderr)
        return 1
    return 0 if captured else 1


if __name__ == "__main__":
    raise SystemExit(main())
