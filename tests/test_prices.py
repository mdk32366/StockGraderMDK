"""Hermetic tests for daily price capture (D-036).

No network, no database. Every payload here is a fixture. What these prove is
the part that must be right before a single live capture runs, because a bad
capture on a given date cannot be re-taken — that is the whole premise of
option (b).
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

import pytest

from ingest.prices import (
    AdjustedOnly,
    DailyBar,
    PriceParseError,
    RawCapture,
    StooqProvider,
    write_capture,
)

GOOD = (
    b"Date,Open,High,Low,Close,Volume\n"
    b"2026-09-24,190.10,192.40,189.55,191.80,54210000\n"
    b"2026-09-25,191.95,194.00,191.20,193.62,61044200\n"
)


def test_parses_unadjusted_daily_csv():
    bars = StooqProvider().parse("aapl", GOOD, captured_on=date(2026, 9, 25))
    assert [b.trade_date for b in bars] == [date(2026, 9, 24), date(2026, 9, 25)]
    assert bars[-1].close == 193.62
    assert bars[-1].volume == 61044200
    assert bars[-1].symbol == "AAPL"


def test_same_day_capture_is_marked_and_earlier_days_are_not():
    """The as-traded guarantee rests on this flag, so it is asserted.

    A bar for today cannot carry a future split adjustment. A bar for an
    earlier date might already have been adjusted by the provider, and the two
    must be distinguishable — otherwise the guarantee quietly covers rows that
    do not have it.
    """
    bars = StooqProvider().parse("aapl", GOOD, captured_on=date(2026, 9, 25))
    by_date = {b.trade_date: b for b in bars}
    assert by_date[date(2026, 9, 25)].captured_same_day is True
    assert by_date[date(2026, 9, 24)].captured_same_day is False


def test_an_adjusted_column_is_refused_not_coerced():
    """§7.1's failure is undetectable downstream, so it is refused at the door."""
    payload = (
        b"Date,Open,High,Low,Close,Adj Close,Volume\n"
        b"2026-09-25,191.95,194.00,191.20,193.62,193.62,61044200\n"
    )
    with pytest.raises(AdjustedOnly, match="adjusted column"):
        StooqProvider().parse("aapl", payload, captured_on=date(2026, 9, 25))


def test_empty_payload_is_an_error_not_a_quiet_no_trade():
    """An unknown symbol returns an empty body. That must not read as a holiday.

    A symbol that silently stops capturing produces a gap shaped exactly like a
    weekend, and nothing downstream distinguishes them.
    """
    with pytest.raises(PriceParseError, match="not evidence"):
        StooqProvider().parse("nope", b"", captured_on=date(2026, 9, 25))


def test_missing_close_column_is_refused():
    payload = b"Date,Open,High,Low,Volume\n2026-09-25,1,2,3,4\n"
    with pytest.raises(PriceParseError, match="expected columns"):
        StooqProvider().parse("aapl", payload, captured_on=date(2026, 9, 25))


def test_header_without_rows_is_refused():
    with pytest.raises(PriceParseError, match="no usable rows"):
        StooqProvider().parse(
            "aapl", b"Date,Open,High,Low,Close,Volume\n",
            captured_on=date(2026, 9, 25),
        )


def test_capture_hashes_the_payload_as_received():
    cap = RawCapture.of("https://example/x", GOOD, "stooq")
    assert cap.content_bytes == len(GOOD)
    assert len(cap.sha256) == 64
    assert cap.sha256 == __import__("hashlib").sha256(GOOD).hexdigest()


def test_write_capture_keeps_the_raw_payload_beside_the_parse(tmp_path):
    """A parser bug six months from now is recoverable only from the raw bytes.

    This data cannot be re-fetched for a past date, so the raw payload is not
    a debugging convenience — it is the only copy.
    """
    provider = StooqProvider()
    cap = RawCapture.of(
        provider.daily_url("aapl"), GOOD, provider.name,
        retrieved_at=datetime(2026, 9, 25, 21, 5, 0, tzinfo=timezone.utc),
    )
    bars = provider.parse("aapl", GOOD, captured_on=date(2026, 9, 25))
    path = write_capture(tmp_path, cap, bars)

    manifest = json.loads(path.read_text(encoding="utf-8"))
    raw = (tmp_path / manifest["raw_file"]).read_bytes()
    assert raw == GOOD

    # fetch_log's columns, named identically, so the loader renames nothing.
    for column in ("url", "retrieved_at", "sha256", "content_bytes"):
        assert column in manifest
    assert manifest["sha256"] == cap.sha256
    assert len(manifest["bars"]) == 2


def test_url_is_built_with_the_us_suffix():
    """A wrong suffix returns an empty body, not an error. Worth pinning."""
    assert StooqProvider().daily_url("AAPL").endswith("s=aapl.us&i=d")


def test_dailybar_has_no_adjusted_field():
    """Structural, not behavioural: there is no column to write one into.

    Refusing adjusted input only helps if there is nowhere for an adjusted
    value to land by accident later.
    """
    assert "adj_close" not in DailyBar.__dataclass_fields__
    assert not any("adj" in f.lower() for f in DailyBar.__dataclass_fields__)


# ---------------------------------------------------------------------------
# YahooChartProvider — added after StooqProvider failed its first live run
# (F-041). Fixtures below are trimmed from a real payload captured 2026-09-25.
# ---------------------------------------------------------------------------

YAHOO = json.dumps({
    "chart": {"result": [{
        "meta": {"currency": "USD", "symbol": "AAPL", "gmtoffset": -14400},
        "timestamp": [1790343000, 1790602200],
        "indicators": {
            "quote": [{
                "open": [338.0, 339.5], "high": [341.0, 342.2],
                "low": [337.1, 338.9], "close": [339.75, 340.13],
                "volume": [51000000, 47250000],
            }],
            "adjclose": [{"adjclose": [338.20, 338.58]}],
        },
    }], "error": None},
}).encode()


def _yahoo_dates():
    from ingest.prices import YahooChartProvider
    bars = YahooChartProvider().parse("AAPL", YAHOO, captured_on=date(2026, 9, 25))
    return [b.trade_date for b in bars]


def test_yahoo_reads_as_traded_close_never_adjclose():
    """The payload carries both. We must take `close`, never `adjclose`."""
    from ingest.prices import YahooChartProvider
    bars = YahooChartProvider().parse("AAPL", YAHOO, captured_on=date(2026, 9, 25))
    closes = [b.close for b in bars]
    assert closes == [339.75, 340.13]
    # The adjusted values must appear nowhere among the as-traded closes.
    assert 338.20 not in closes and 338.58 not in closes


def test_yahoo_records_the_adjustment_separately_with_a_factor():
    """§7.1: as-traded and adjustment stored separately, not folded together."""
    from ingest.prices import YahooChartProvider
    bars, adjustments = YahooChartProvider().parse_both(
        "AAPL", YAHOO, captured_on=date(2026, 9, 25))
    assert len(adjustments) == len(bars) == 2
    a = adjustments[-1]
    assert a.as_traded_close == 340.13
    assert a.adjusted_close == 338.58
    assert a.factor == pytest.approx(338.58 / 340.13)
    assert a.observed_on == date(2026, 9, 25)


def test_yahoo_uses_exchange_local_date_not_utc():
    """A daily bar belongs to the exchange's session, not to UTC.

    THE FIXTURE IS CHOSEN SO THE TWO ANSWERS DIFFER. A 09:30 ET session is
    13:30 UTC, and UTC-vs-local give the SAME date there - so a test built on
    an ordinary session cannot fail for the reason it claims, which is the
    register's first failure shape. This timestamp is 2026-09-26 01:00 UTC,
    which at gmtoffset -14400 is 2026-09-25 21:00 locally: UTC says the 26th,
    the exchange says the 25th.
    """
    from ingest.prices import YahooChartProvider
    payload = json.dumps({"chart": {"result": [{
        "meta": {"gmtoffset": -14400},
        "timestamp": [1790384400],          # 2026-09-26 01:00 UTC
        "indicators": {"quote": [{"close": [100.0]}]},
    }], "error": None}}).encode()
    bars = YahooChartProvider().parse("AAPL", payload,
                                      captured_on=date(2026, 9, 25))
    assert bars[0].trade_date == date(2026, 9, 25), "took the UTC date"
    assert bars[0].captured_same_day is True


def test_yahoo_ordinary_session_dates():
    assert _yahoo_dates() == [date(2026, 9, 25), date(2026, 9, 28)]


def test_yahoo_adjclose_without_close_is_refused():
    """The §7.1 refusal, in this provider's shape."""
    from ingest.prices import AdjustedOnly, YahooChartProvider
    payload = json.dumps({"chart": {"result": [{
        "meta": {"gmtoffset": 0}, "timestamp": [1758807000],
        "indicators": {"quote": [{}], "adjclose": [{"adjclose": [338.2]}]},
    }], "error": None}}).encode()
    with pytest.raises(AdjustedOnly, match="no as-traded close"):
        YahooChartProvider().parse("AAPL", payload, captured_on=date(2026, 9, 25))


def test_yahoo_unknown_symbol_is_an_error_not_a_quiet_no_trade():
    from ingest.prices import PriceParseError, YahooChartProvider
    payload = json.dumps({"chart": {"result": [], "error": None}}).encode()
    with pytest.raises(PriceParseError, match="not evidence"):
        YahooChartProvider().parse("NOPE", payload, captured_on=date(2026, 9, 25))


def test_yahoo_non_json_is_refused():
    """Stooq's failure mode was an HTML challenge page. Guard against it here."""
    from ingest.prices import PriceParseError, YahooChartProvider
    with pytest.raises(PriceParseError, match="not JSON"):
        YahooChartProvider().parse(
            "AAPL", b"<!DOCTYPE html><html><body>verify your browser</body></html>",
            captured_on=date(2026, 9, 25))


def test_two_symbols_with_identical_payloads_do_not_overwrite(tmp_path):
    """F-042. The filename must carry the symbol.

    Before the fix the name was provider + payload-hash + second, so two
    captures in the same second with byte-identical payloads produced one file
    instead of two -- a silent overwrite, a capture vanishing with no evidence
    it arrived. In production the payloads differ because the symbol is inside
    the JSON, which made the old scheme correct BY ACCIDENT. This asserts it is
    correct by construction.
    """
    from ingest.prices import RawCapture, write_capture

    body = b"identical"
    at = datetime(2026, 9, 25, 19, 0, 0, tzinfo=timezone.utc)
    for sym in ("AAPL", "MSFT"):
        cap = RawCapture.of(f"https://example/{sym}", body, "p", retrieved_at=at)
        bar = DailyBar(symbol=sym, trade_date=date(2026, 9, 25), open=None,
                       high=None, low=None, close=1.0, volume=None,
                       captured_same_day=True)
        write_capture(tmp_path, cap, [bar])

    names = sorted(p.name for p in tmp_path.glob("*.json"))
    assert len(names) == 2, f"a capture was overwritten: {names}"
    assert names[0].startswith("AAPL-") and names[1].startswith("MSFT-")
