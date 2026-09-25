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


@dataclass(frozen=True)
class AdjustmentObservation:
    """The adjustment, kept in a separate record from the as-traded bar.

    §7.1 says *store the as-traded close and the adjustment factors
    separately*. This is that separation made structural rather than
    conventional: ``DailyBar`` has no field an adjusted value can occupy, so
    the only way to record one is here, where it is labelled.

    ``factor`` is adjusted / as-traded on the day of observation — the
    cumulative split-and-dividend adjustment the provider has applied so far.
    It is a property of *when it was read*, not of the trading day, which is
    why ``observed_on`` is part of the record.
    """

    symbol: str
    trade_date: date
    as_traded_close: float
    adjusted_close: float
    observed_on: date

    @property
    def factor(self) -> float | None:
        if not self.as_traded_close:
            return None
        return self.adjusted_close / self.as_traded_close

    def as_row(self) -> dict:
        d = asdict(self)
        d["trade_date"] = self.trade_date.isoformat()
        d["observed_on"] = self.observed_on.isoformat()
        d["factor"] = self.factor
        return d


class YahooChartProvider:
    """Yahoo's chart endpoint. JSON, no API key, as-traded and adjusted split.

    WHY THIS EXISTS: StooqProvider was the first implementation and **it does
    not work from a script.** A live run on 2026-09-25 returned a 796-byte
    JavaScript browser-verification page for all ten symbols — see F-041. The
    parser refused all ten rather than storing the challenge page as prices,
    which is the behaviour, but it captured nothing.

    This endpoint returns ``close`` and ``adjclose`` in **separate arrays**,
    which is §7.1's requirement handed to us by the source. We read ``close``
    and never ``adjclose``; the adjusted value is recorded only as an
    ``AdjustmentObservation``, where it is labelled for what it is.

    **This is not a vendor-of-record decision and must not be read as one.**
    OPEN-9 is open, D-036 is provisional, and the endpoint is undocumented —
    it can change or close without notice. It is here because capture is
    deadline-bearing and this is what works today without a credential.
    """

    name = "yahoo-chart"

    def daily_url(self, symbol: str) -> str:
        return (f"https://query1.finance.yahoo.com/v8/finance/chart/"
                f"{symbol.upper()}?interval=1d&range=5d")

    def parse(self, symbol: str, payload: bytes, captured_on: date
              ) -> list[DailyBar]:
        bars, _ = self.parse_both(symbol, payload, captured_on)
        return bars

    def parse_both(self, symbol: str, payload: bytes, captured_on: date
                   ) -> tuple[list[DailyBar], list[AdjustmentObservation]]:
        try:
            doc = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PriceParseError(f"{symbol}: payload is not JSON") from exc

        chart = doc.get("chart") or {}
        if chart.get("error"):
            raise PriceRefused(f"{symbol}: {chart['error']}")
        results = chart.get("result") or []
        if not results:
            # Same rule as the empty CSV body: an unknown symbol must not read
            # as a day with no trading.
            raise PriceParseError(
                f"{symbol}: no result in payload. This is an unknown or "
                f"unavailable symbol, not evidence that no trade occurred."
            )

        r = results[0]
        meta = r.get("meta") or {}
        stamps = r.get("timestamp") or []
        quote = ((r.get("indicators") or {}).get("quote") or [{}])[0]
        closes = quote.get("close")

        if closes is None:
            adj_block = (r.get("indicators") or {}).get("adjclose")
            if adj_block:
                raise AdjustedOnly(
                    f"{symbol}: payload carries adjclose but no as-traded "
                    f"close. Refusing - an adjusted close in the as-traded "
                    f"field is undetectable downstream (§7.1)."
                )
            raise PriceParseError(f"{symbol}: no close series in payload")

        adj_series = (((r.get("indicators") or {}).get("adjclose")
                       or [{}])[0]).get("adjclose") or []

        # Exchange-local date, not UTC date. A daily bar is stamped at the
        # exchange's session, and deriving the trading day from UTC would
        # misdate any exchange far enough east or west.
        offset = int(meta.get("gmtoffset") or 0)

        bars: list[DailyBar] = []
        adjustments: list[AdjustmentObservation] = []

        for i, ts in enumerate(stamps):
            close = closes[i] if i < len(closes) else None
            if ts is None or close is None:
                continue
            trade_date = datetime.fromtimestamp(
                int(ts) + offset, tz=timezone.utc).date()

            bars.append(DailyBar(
                symbol=symbol.upper(),
                trade_date=trade_date,
                open=_index(quote.get("open"), i),
                high=_index(quote.get("high"), i),
                low=_index(quote.get("low"), i),
                close=float(close),
                volume=(int(v) if (v := _index(quote.get("volume"), i))
                        is not None else None),
                captured_same_day=(trade_date == captured_on),
            ))

            adj = _index(adj_series, i)
            if adj is not None:
                adjustments.append(AdjustmentObservation(
                    symbol=symbol.upper(),
                    trade_date=trade_date,
                    as_traded_close=float(close),
                    adjusted_close=float(adj),
                    observed_on=captured_on,
                ))

        if not bars:
            raise PriceParseError(f"{symbol}: parsed but no usable rows")
        return bars, adjustments


def _index(seq, i):
    if not seq or i >= len(seq):
        return None
    v = seq[i]
    return None if v is None else float(v)


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


def write_capture(out_dir: Path, capture: RawCapture, bars: Iterable[DailyBar],
                  adjustments: Iterable[AdjustmentObservation] | None = None
                  ) -> Path:
    """Write one symbol's capture: the raw payload, and the parsed bars.

    The raw payload is kept alongside the parse. A parser bug found in six
    months is recoverable from what was stored; it is not recoverable from
    parsed output alone, and this data cannot be re-fetched for a past date.
    That asymmetry is the entire argument for keeping both.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    bars = list(bars)
    stamp = capture.retrieved_at.strftime("%Y%m%dT%H%M%SZ")

    # THE SYMBOL IS IN THE FILENAME, AND IT HAS TO BE.
    # Without it the name is provider + payload hash + second, which collides
    # for any two captures in the same second with identical payloads -- and a
    # collision here OVERWRITES, silently, losing a capture with no evidence it
    # ever arrived. In production two symbols' payloads differ because the
    # symbol is inside the JSON, so the old scheme worked by accident rather
    # than by construction. That is the distinction 0001's uniqueness key exists
    # to make, one layer out. See F-042.
    symbol = bars[0].symbol if bars else "UNKNOWN"
    base = f"{symbol}-{capture.provider}-{capture.sha256[:12]}-{stamp}"

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
        # Separate key, not a column on the bar. §7.1 requires the adjustment
        # stored separately from the as-traded close, and a separate key is
        # how that survives a careless loader.
        "adjustments": [a.as_row() for a in (adjustments or [])],
    }
    path = out_dir / f"{base}.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True),
                    encoding="utf-8")
    return path
