"""Hermetic tests for ingest slice 1.

No network, no database. Parsing, the rate limit, 403 handling and the scheme
refusal are all testable without either, which is why they are in the gate.

Loading into Postgres and double-ingest idempotency are non-hermetic and live on
the testplan's non-hermetic track. A green here is not evidence that ingest
loads.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import urllib.error
from datetime import date
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _REPO / "ingest" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


edgar = _load("edgar")
slice1 = _load("slice1")


# ---------------------------------------------------------------------------
# D-023: the rate limit is a constant you can point at
# ---------------------------------------------------------------------------

def test_published_limit_is_recorded():
    assert edgar.SEC_MAX_REQUESTS_PER_SECOND == 10
    assert edgar.TARGET_REQUESTS_PER_SECOND <= edgar.SEC_MAX_REQUESTS_PER_SECOND


def test_limiter_refuses_a_rate_above_the_published_maximum():
    """The limit is not a tuning parameter."""
    with pytest.raises(ValueError, match="exceeds the SEC published maximum"):
        edgar.RateLimiter(requests_per_second=50)


def test_limiter_enforces_the_minimum_interval():
    slept: list[float] = []
    ticks = iter([0.0, 0.0, 0.01, 0.01])
    lim = edgar.RateLimiter(requests_per_second=5,
                            sleep=slept.append, clock=lambda: next(ticks))
    lim.wait()          # first call: no wait
    assert slept == []
    lim.wait()          # 0.01s later, interval is 0.2s -> must sleep 0.19s
    assert slept and abs(slept[0] - 0.19) < 1e-9


def test_user_agent_without_contact_details_is_refused():
    """A User-Agent without contact details is what earns the 403."""
    with pytest.raises(ValueError, match="contact details"):
        edgar.EdgarClient(user_agent="StockGraderMDK")


# ---------------------------------------------------------------------------
# D-023: no retry that hides a 403
# ---------------------------------------------------------------------------

def _http_error(code):
    def opener(request):
        raise urllib.error.HTTPError(request.full_url, code, "boom", {}, None)
    return opener


def test_403_raises_immediately_and_is_never_retried():
    attempts = []

    def opener(request):
        attempts.append(request.full_url)
        raise urllib.error.HTTPError(request.full_url, 403, "Forbidden", {}, None)

    client = edgar.EdgarClient(opener=opener, sleep=lambda _: None,
                               limiter=edgar.RateLimiter(10, sleep=lambda _: None))
    with pytest.raises(edgar.EdgarRefused, match="refusal, not a transient"):
        client.fetch("https://data.sec.gov/anything")
    assert len(attempts) == 1, "a 403 must not be retried"


@pytest.mark.parametrize("code", [429, 503])
def test_429_and_503_are_retried_then_give_up(code):
    attempts = []

    def opener(request):
        attempts.append(code)
        raise urllib.error.HTTPError(request.full_url, code, "slow down", {}, None)

    client = edgar.EdgarClient(opener=opener, sleep=lambda _: None,
                               limiter=edgar.RateLimiter(10, sleep=lambda _: None))
    with pytest.raises(edgar.EdgarUnavailable):
        client.fetch("https://data.sec.gov/anything")
    assert len(attempts) == edgar.MAX_RETRIES + 1


def test_fetch_carries_provenance():
    class _Resp:
        def __init__(self, body): self._b = body
        def read(self): return self._b
        def __enter__(self): return self
        def __exit__(self, *a): return False

    client = edgar.EdgarClient(opener=lambda r: _Resp(b"hello"),
                               limiter=edgar.RateLimiter(10, sleep=lambda _: None))
    f = client.fetch("https://data.sec.gov/x")
    assert f.url == "https://data.sec.gov/x"
    assert f.sha256 == (
        "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    )
    assert f.retrieved_at.tzinfo is not None, "timestamp must be tz-aware"


# ---------------------------------------------------------------------------
# The scheme assumption fails loudly (handover §5)
# ---------------------------------------------------------------------------

def test_non_cik_scheme_is_refused_not_coerced():
    with pytest.raises(slice1.IngestError, match="is not 'http://www.sec.gov/CIK'"):
        slice1.parse_entity_identifier("http://standards.iso.org/iso/17442", "5493001KJTIIGC8Y1R12")


def test_cik_scheme_is_accepted():
    assert slice1.parse_entity_identifier(slice1.SEC_CIK_SCHEME, "0000320193") == 320193


@pytest.mark.parametrize("bad", ["", "abc", "-1", "0"])
def test_malformed_cik_is_refused(bad):
    with pytest.raises(slice1.IngestError):
        slice1.parse_entity_identifier(slice1.SEC_CIK_SCHEME, bad)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

SUBMISSIONS = json.dumps({
    "cik": 320193,
    "name": "Apple Inc.",
    "sic": "3571",
    "sicDescription": "Electronic Computers",
    "filings": {"recent": {
        "accessionNumber": ["0000320193-23-000106", "0000320193-24-000010"],
        "form": ["10-K", "10-K/A"],
        "filingDate": ["2023-11-03", "2024-02-01"],
        "reportDate": ["2023-09-30", "2023-09-30"],
    }},
})


def test_parse_submissions_maps_entity_sic_to_current_not_at_filing():
    filer, filings = slice1.parse_submissions(SUBMISSIONS, as_of=date(2026, 9, 23))
    assert filer.cik == 320193
    assert filer.current_sic == "3571"
    assert filer.metadata_as_of == date(2026, 9, 23)
    # OPEN-32: there is no per-filing SIC to map, so FilingRow carries none.
    assert not hasattr(filings[0], "sic_at_filing")


def test_amendment_is_derived_from_form_type_and_stored():
    _, filings = slice1.parse_submissions(SUBMISSIONS, as_of=date(2026, 9, 23))
    assert [f.is_amendment for f in filings] == [False, True]


def test_period_of_report_is_distinct_from_filing_date():
    """Conflating them is the lookahead bug."""
    _, filings = slice1.parse_submissions(SUBMISSIONS, as_of=date(2026, 9, 23))
    f = filings[0]
    assert f.filing_date == date(2023, 11, 3)
    assert f.period_of_report == date(2023, 9, 30)


def test_malformed_accession_is_refused_at_parse_time():
    doc = json.loads(SUBMISSIONS)
    doc["filings"]["recent"]["accessionNumber"][0] = "not-an-accession"
    with pytest.raises(slice1.IngestError, match="does not match EDGAR's format"):
        slice1.parse_submissions(json.dumps(doc), as_of=date(2026, 9, 23))


def test_parse_company_tickers_stamps_observation_date_not_a_start_date():
    doc = json.dumps({"0": {"cik_str": 320193, "ticker": "aapl", "title": "Apple Inc."}})
    rows = slice1.parse_company_tickers(doc, as_of=date(2026, 9, 23))
    assert len(rows) == 1
    assert rows[0].ticker == "AAPL"
    # valid_from is when we SAW it, not when it began. The file carries no start
    # date, so claiming one would be inventing history.
    assert rows[0].valid_from == date(2026, 9, 23)
    assert rows[0].valid_to is None


def test_entries_without_a_ticker_are_skipped_not_inserted_blank():
    doc = json.dumps({"0": {"cik_str": 320193, "ticker": "", "title": "X"}})
    assert slice1.parse_company_tickers(doc, as_of=date(2026, 9, 23)) == []


# ---------------------------------------------------------------------------
# The ticker files are not the universe (P-10) — asserted as a test so the
# claim cannot quietly stop being true.
# ---------------------------------------------------------------------------

def test_ticker_parsing_produces_no_filings_and_no_universe():
    """A crosswalk yields identifiers, never filing history.

    If someone later makes parse_company_tickers emit FilingRows, the universe
    silently becomes current-listing-only again. This is that regression,
    written down.
    """
    doc = json.dumps({"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple"}})
    rows = slice1.parse_company_tickers(doc, as_of=date(2026, 9, 23))
    assert all(isinstance(r, slice1.TickerRow) for r in rows)
