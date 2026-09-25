"""Daily as-traded price capture — D-036 (TDD v3 §17.5 option b), implemented.

WHY THIS EXISTS AND WHY IT COULD NOT WAIT
-----------------------------------------
§17.5 is the only open question in this project whose cost is elapsed time. A
back-adjusted price series restates history for splits and dividends, and
``gqs-source-map.md`` §7.1 states the consequence: a back-adjusted close times
shares outstanding gives a market cap nobody ever observed, and **it passes
every test that does not check for it specifically.** No vendor sells the
unadjusted series as it stood on a past date, so a day not captured cannot be
bought later at any price, from anyone.

THE PROPERTY THAT MAKES THE VENDOR CHOICE DEFERRABLE
-----------------------------------------------------
**A close captured on the day it traded is as-traded by construction.** Split
and dividend adjustments are applied retroactively, so today's close cannot yet
have had a future adjustment applied to it. This is the whole reason D-036 could
be ruled ahead of OPEN-9: capture is *provider-agnostic* in a way that
backfilling never is. What we write down today stays true whoever we later pay.

That property is load-bearing, so it is asserted rather than assumed:
``DailyBar.captured_same_day`` records whether the bar's trade date equals the
capture date, and a bar captured for an *earlier* date is flagged rather than
silently mixed in with bars that carry the guarantee.

WHAT THIS MODULE REFUSES TO DO
-------------------------------
It never writes an adjusted close into the as-traded field. A provider that
serves only adjusted prices raises ``AdjustedOnly`` rather than having its
output coerced — the same shape as D-023's "no retry that hides a 403". A
silently adjusted series is exactly the defect §7.1 exists to prevent, and it
would be undetectable downstream.

It does not touch the database. D-036 records that capture to disk may begin
before the schema lands, because *the dates are the perishable part, not the
loading*. The on-disk manifest mirrors ``fetch_log``'s columns (url,
retrieved_at, sha256, content_bytes) so the eventual migration loads it without
reshaping anything.

This module lives outside ``app/``. The web process is read-only against
Postgres (D-031) and must not be able to import an ingestion path.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable, Protocol


class PriceRefused(RuntimeError):
    """The provider refused the request. Never retried blind. See D-023."""


class AdjustedOnly(RuntimeError):
    """The provider serves adjusted prices only.

    Raised rather than coerced. An adjusted close in the as-traded column is
    the precise failure gqs-source-map.md §7.1 describes, and nothing
    downstream can detect it.
    """


class PriceParseError(ValueError):
    """The payload did not have the shape the provider promised."""


@dataclass(frozen=True)
class DailyBar:
    """One symbol, one trading day, as traded.

    ``close`` is the as-traded close. There is deliberately no ``adj_close``
    field: this module does not carry adjusted prices at all, so there is no
    column for one to be written into by mistake. Adjustment factors, when a
    provider supplies them, belong in a separate record — §7.1 requires them
    stored separately, not folded in.
    """

    symbol: str
    trade_date: date
    open: float | None
    high: float | None
    low: float | None
    close: float
    volume: int | None
    # True when trade_date == the UTC date of capture. The as-traded guarantee
    # rests on this; a bar captured for an earlier date may already have been
    # adjusted by the provider and does NOT carry the guarantee.
    captured_same_day: bool

    def as_row(self) -> dict:
        d = asdict(self)
        d["trade_date"] = self.trade_date.isoformat()
        return d


@dataclass(frozen=True)
class RawCapture:
    """A payload exactly as received, plus fetch_log's four columns.

    Field names match ``fetch_log`` (0002) on purpose. The loader that lands
    these in Postgres should not have to rename anything, because a rename is a
    place for a value to change meaning silently.
    """

    url: str
    retrieved_at: datetime
    sha256: str
    content_bytes: int
    payload: bytes
    provider: str

    @staticmethod
    def of(url: str, payload: bytes, provider: str,
           *, retrieved_at: datetime | None = None) -> "RawCapture":
        return RawCapture(
            url=url,
            retrieved_at=retrieved_at or datetime.now(timezone.utc),
            sha256=hashlib.sha256(payload).hexdigest(),
            content_bytes=len(payload),
            payload=payload,
            provider=provider,
        )


class PriceProvider(Protocol):
    """The seam that keeps OPEN-9 out of this module.

    D-036 is explicitly provisional: it selects no vendor of record. So the
    provider is an interface with one implementation, and swapping it later
    does not invalidate a single captured row.
    """

    name: str

    def daily_url(self, symbol: str) -> str: ...

    def parse(self, symbol: str, payload: bytes, captured_on: date
              ) -> list[DailyBar]: ...


class StooqProvider:
    """Stooq daily CSV. No API key, and it serves UNADJUSTED closes.

    Chosen as the first implementation because it needs no credential — which
    matters here, since no credential reaches the Builder — and because its
    daily series is not back-adjusted. It is **not** a vendor-of-record
    decision: OPEN-9 remains open and D-036 says so.

    Column shape, from the documented CSV header:
        Date,Open,High,Low,Close,Volume
    """

    name = "stooq"

    # Stooq's US symbols carry a .us suffix. Kept explicit rather than
    # hidden in a format string, because a wrong suffix returns an empty
    # body rather than an error, and an empty body must not read as "no
    # trading today".
    SUFFIX = ".us"

    def daily_url(self, symbol: str) -> str:
        return f"https://stooq.com/q/d/l/?s={symbol.lower()}{self.SUFFIX}&i=d"

    def parse(self, symbol: str, payload: bytes, captured_on: date
              ) -> list[DailyBar]:
        text = payload.decode("utf-8", errors="strict").strip()

        # An empty body is how this provider reports an unknown symbol. It is
        # NOT a market holiday and must never be recorded as one: a symbol that
        # silently stops capturing is a gap that looks like a weekend.
        if not text:
            raise PriceParseError(
                f"{symbol}: empty payload. Stooq returns an empty body for an "
                f"unknown symbol; this is not evidence that no trade occurred."
            )

        reader = csv.DictReader(io.StringIO(text))
        header = reader.fieldnames or []

        # Refuse rather than coerce. If the provider ever starts serving an
        # adjusted series, the column name is the only warning we get.
        for field in header:
            if "adj" in field.lower():
                raise AdjustedOnly(
                    f"{symbol}: payload carries an adjusted column {field!r}. "
                    f"Refusing — an adjusted close in the as-traded field is "
                    f"undetectable downstream (gqs-source-map.md §7.1)."
                )

        required = {"Date", "Close"}
        if not required.issubset(set(header)):
            raise PriceParseError(
                f"{symbol}: expected columns {sorted(required)}, got {header}"
            )

        bars: list[DailyBar] = []
        for row in reader:
            raw_date = (row.get("Date") or "").strip()
            raw_close = (row.get("Close") or "").strip()
            if not raw_date or not raw_close:
                continue
            try:
                trade_date = date.fromisoformat(raw_date)
                close = float(raw_close)
            except ValueError as exc:
                raise PriceParseError(f"{symbol}: bad row {row!r}") from exc

            bars.append(DailyBar(
                symbol=symbol.upper(),
                trade_date=trade_date,
                open=_maybe_float(row.get("Open")),
                high=_maybe_float(row.get("High")),
                low=_maybe_float(row.get("Low")),
                close=close,
                volume=_maybe_int(row.get("Volume")),
                captured_same_day=(trade_date == captured_on),
            ))

        if not bars:
            raise PriceParseError(
                f"{symbol}: header parsed but no usable rows"
            )
        return bars


def _maybe_float(v: str | None) -> float | None:
    v = (v or "").strip()
    if not v or v == "N/A":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def _maybe_int(v: str | None) -> int | None:
    v = (v or "").strip()
    if not v or v == "N/A":
        return None
    try:
        return int(float(v))
    except ValueError:
        return None


def write_capture(out_dir: Path, capture: RawCapture, bars: Iterable[DailyBar]
                  ) -> Path:
    """Write one symbol's capture: the raw payload, and the parsed bars.

    The raw payload is kept alongside the parse. A parser bug found in six
    months is recoverable from what was stored; it is not recoverable from
    parsed output alone, and this data cannot be re-fetched for a past date.
    That asymmetry is the entire argument for keeping both.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = capture.retrieved_at.strftime("%Y%m%dT%H%M%SZ")
    base = f"{capture.provider}-{capture.sha256[:12]}-{stamp}"

    (out_dir / f"{base}.raw").write_bytes(capture.payload)

    manifest = {
        # fetch_log's columns, named identically (0002).
        "url": capture.url,
        "retrieved_at": capture.retrieved_at.isoformat(),
        "sha256": capture.sha256,
        "content_bytes": capture.content_bytes,
        "provider": capture.provider,
        "raw_file": f"{base}.raw",
        "bars": [b.as_row() for b in bars],
    }
    path = out_dir / f"{base}.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True),
                    encoding="utf-8")
    return path
