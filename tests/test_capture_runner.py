"""The capture runner's exit codes (D-036, daily schedule).

These matter more than they look. `.github/workflows/capture-prices.yml` runs
this ~250 times a year and branches on the exit code: 1 fails the run, 3 warns,
0 is quiet. About nine of those runs land on market holidays.

Get the codes wrong in one direction and the schedule cries wolf nine times a
year until somebody stops reading it. Get them wrong in the other and a stale
provider is indistinguishable from a closed market — which is the conflation
this whole module exists to refuse. So they are tested.

No network: `fetch` is replaced in every test here.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "capture_prices", _REPO / "tools" / "capture_prices.py")
capture_prices = importlib.util.module_from_spec(_spec)
sys.modules["capture_prices"] = capture_prices
_spec.loader.exec_module(capture_prices)


@pytest.fixture(autouse=True)
def _no_rate_limit_sleep(monkeypatch):
    """The runner paces itself at 2 req/s. That is correct against a live
    endpoint and pure cost here -- ten symbols would add five seconds to every
    gate run, and a slow suite is a suite people stop running."""
    monkeypatch.setattr(capture_prices.time, "sleep", lambda *_: None)


def _yahoo_payload(days_ago: int) -> bytes:
    """A payload whose single bar is `days_ago` days before today (UTC)."""
    when = datetime.now(timezone.utc) - timedelta(days=days_ago)
    # Midday UTC keeps the bar on `when`'s date at gmtoffset 0.
    ts = int(when.replace(hour=12, minute=0, second=0,
                          microsecond=0).timestamp())
    return json.dumps({"chart": {"result": [{
        "meta": {"gmtoffset": 0, "currency": "USD"},
        "timestamp": [ts],
        "indicators": {
            "quote": [{"open": [1.0], "high": [2.0], "low": [0.5],
                       "close": [1.5], "volume": [1000]}],
            "adjclose": [{"adjclose": [1.5]}],
        },
    }], "error": None}}).encode()


def test_exit_0_when_a_same_day_bar_is_captured(tmp_path, monkeypatch):
    monkeypatch.setattr(capture_prices, "fetch", lambda url, **kw: _yahoo_payload(0))
    code = capture_prices.main(
        ["--symbols", "AAPL", "--out", str(tmp_path), "--live"])
    assert code == 0
    assert list(tmp_path.glob("*.json")), "expected a manifest on disk"


def test_exit_3_when_data_arrives_but_no_bar_is_same_day(tmp_path, monkeypatch):
    """A market holiday looks exactly like this. So does a stale provider.

    3 rather than 1, because nine false alarms a year train people to ignore
    the alert. 3 rather than 0, because the series did not advance and that
    must not be silent.
    """
    monkeypatch.setattr(capture_prices, "fetch", lambda url, **kw: _yahoo_payload(4))
    code = capture_prices.main(
        ["--symbols", "AAPL", "--out", str(tmp_path), "--live"])
    assert code == 3
    # Data was still written. Exit 3 is "did not advance", not "discard".
    assert list(tmp_path.glob("*.json"))


def test_exit_1_when_nothing_is_captured(tmp_path, monkeypatch):
    def refuse(url, **kw):
        raise capture_prices.PriceRefused(f"{url}: HTTP 429")

    monkeypatch.setattr(capture_prices, "fetch", refuse)
    code = capture_prices.main(
        ["--symbols", "AAPL,MSFT", "--out", str(tmp_path), "--live"])
    assert code == 1
    assert not list(tmp_path.glob("*.json")), "nothing should be written"


def test_a_refused_symbol_does_not_abort_the_others(tmp_path, monkeypatch):
    """One bad symbol must not cost the whole day's capture."""
    def selective(url, **kw):
        if "MSFT" in url:
            raise capture_prices.PriceRefused(f"{url}: HTTP 404")
        return _yahoo_payload(0)

    monkeypatch.setattr(capture_prices, "fetch", selective)
    code = capture_prices.main(
        ["--symbols", "AAPL,MSFT,NVDA", "--out", str(tmp_path), "--live"])
    assert code == 0
    assert len(list(tmp_path.glob("*.json"))) == 2


def test_dry_run_writes_nothing_and_never_calls_fetch(tmp_path, monkeypatch):
    def explode(url, **kw):
        raise AssertionError("dry run must not reach the network")

    monkeypatch.setattr(capture_prices, "fetch", explode)
    assert capture_prices.main(
        ["--symbols", "AAPL", "--out", str(tmp_path), "--dry-run"]) == 0
    assert not list(tmp_path.glob("*"))


def test_live_is_required_for_a_fetch(tmp_path, monkeypatch):
    """Absence of --live is a dry run, not an error. The default is safe."""
    def explode(url, **kw):
        raise AssertionError("no --live must not reach the network")

    monkeypatch.setattr(capture_prices, "fetch", explode)
    assert capture_prices.main(
        ["--symbols", "AAPL", "--out", str(tmp_path)]) == 0


def test_the_shipped_symbol_file_parses_and_skips_comments(tmp_path, monkeypatch):
    """The workflow feeds this exact file. A comment read as a ticker is a
    refusal every single day, forever, and nobody would look."""
    seen: list[str] = []

    def record(url, **kw):
        seen.append(url)
        return _yahoo_payload(0)

    monkeypatch.setattr(capture_prices, "fetch", record)
    code = capture_prices.main([
        "--symbol-file", str(_REPO / "ingest" / "universe" / "symbols.txt"),
        "--out", str(tmp_path), "--live"])
    assert code == 0
    assert len(seen) == 10
    assert not any("#" in u for u in seen)
