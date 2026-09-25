"""Ingest slice 1 — filers, tickers and filings. No facts.

Sources, ruled in D15 (`D-next/ingest-sources`):

    filer, filing   <- submissions.zip   (all filers, full history)
    filer_ticker    <- company_tickers*.json  (current-day crosswalk ONLY)

The ticker files are **not** the universe. Measured 2026-09-23 they hold 8,049
distinct CIKs, every one currently listed — Lehman, Sears, Bed Bath & Beyond and
Enron are all absent. A universe seeded from them cannot contain a company that
stopped trading, which is the survivorship bias ruling 5 exists to close. They
are the identifier crosswalk and nothing else (P-10).

PROVENANCE
----------
Every row written here carries the fetch it was derived from (0002,
`source_fetch_id`, NOT NULL). The fetch is recorded first, in the same
transaction as the rows it produces, so a failure takes both. D-023's claim -
that raw filings need not be stored because accession plus hash makes any row
re-derivable - is true of this data rather than aspirational.

IDEMPOTENCY IS THE SCHEMA'S, NOT THIS MODULE'S
----------------------------------------------
Every insert is `ON CONFLICT DO NOTHING` against a real constraint. Re-running
the loader changes nothing, and that is a property of the keys rather than of
bookkeeping here. `fact_one_per_filing`'s reasoning applies to these tables too:
the conflict target can only ever fire for a genuine re-ingest.

WHAT THIS MODULE DOES NOT CLAIM
-------------------------------
It does not exercise A8. `entity_cik` is not written here — slice 1 has no facts
— and even in the fact slice, drawing from a per-CIK source makes the entity
trivially the CIK that was requested, so the co-registrant case never arises.
A8 and the co-registrant fixture remain the only evidence for OPEN-29's fix.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date

# The SEC identifies entities by CIK. An identifier under any other scheme must
# make ingest FAIL rather than be coerced into a bigint column that means CIK.
SEC_CIK_SCHEME = "http://www.sec.gov/CIK"

_ACCESSION = re.compile(r"^\d{10}-\d{2}-\d{6}$")


class IngestError(RuntimeError):
    """Refuse rather than coerce. Every raise here is a row we will not invent."""


def parse_entity_identifier(scheme: str, value: str) -> int:
    """Turn an XBRL context entity identifier into a CIK, or refuse.

    Built in slice 1 although slice 1 writes no facts, because the assumption it
    enforces was stated in 0001's column comment and an assumption stated in a
    comment and never tested is exactly the shape the register keeps finding.

    Anything not under the SEC CIK scheme raises. It is not coerced, not
    defaulted, and not dropped with a warning — a warning in a log is a row
    silently missing from a universe.
    """
    if scheme != SEC_CIK_SCHEME:
        raise IngestError(
            f"entity identifier scheme {scheme!r} is not {SEC_CIK_SCHEME!r}. "
            "fact.entity_cik means CIK; coercing a foreign scheme into it would "
            "assert an identity we cannot support. Ingest fails here "
            "deliberately."
        )
    digits = value.strip()
    if not digits.isdigit():
        raise IngestError(f"CIK identifier {value!r} is not numeric")
    cik = int(digits)
    if cik <= 0:
        raise IngestError(f"CIK identifier {value!r} is not positive")
    return cik


@dataclass(frozen=True)
class FilerRow:
    cik: int
    current_name: str
    current_sic: str | None
    current_sic_desc: str | None
    metadata_as_of: date


@dataclass(frozen=True)
class FilingRow:
    accession: str
    cik: int
    form_type: str
    filing_date: date
    period_of_report: date | None
    is_amendment: bool
    # sic_at_filing is deliberately absent. OPEN-32: the submissions document
    # carries SIC at ENTITY level only; none of its 16 per-filing columns carry
    # one. Filling the point-in-time column from the entity's CURRENT SIC would
    # put today's classification in a column whose name asserts it is not
    # today's, invisibly and permanently. It stays NULL.


@dataclass(frozen=True)
class TickerRow:
    cik: int
    ticker: str
    exchange: str | None
    valid_from: date
    valid_to: None = None


def _as_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def parse_submissions(document: bytes | str, *, as_of: date) -> tuple[FilerRow, list[FilingRow]]:
    """Parse one filer's submissions document into rows.

    `as_of` stamps `filer.metadata_as_of`, because the `current_*` columns are a
    claim about a moment and an unbounded "current" is not a claim at all.
    """
    if isinstance(document, bytes):
        document = document.decode("utf-8")
    d = json.loads(document)

    cik = parse_entity_identifier(SEC_CIK_SCHEME, str(d["cik"]))
    filer = FilerRow(
        cik=cik,
        current_name=d["name"],
        current_sic=(d.get("sic") or None),
        current_sic_desc=(d.get("sicDescription") or None),
        metadata_as_of=as_of,
    )

    filings: list[FilingRow] = []
    recent = d.get("filings", {}).get("recent", {})
    accessions = recent.get("accessionNumber", [])
    for i, accession in enumerate(accessions):
        if not _ACCESSION.match(accession):
            raise IngestError(
                f"accession {accession!r} does not match EDGAR's format. The "
                "schema's CHECK would reject it; refusing here gives a better "
                "message than a constraint violation 400,000 rows in."
            )
        form = recent["form"][i]
        filings.append(
            FilingRow(
                accession=accession,
                cik=cik,
                form_type=form,
                filing_date=_as_date(recent["filingDate"][i]),
                period_of_report=_as_date(recent.get("reportDate", [None] * len(accessions))[i]),
                # Derived at ingest and STORED, per 0001's comment: a later
                # change in how we detect amendments must not silently restate
                # history.
                is_amendment=form.endswith("/A"),
            )
        )
    return filer, filings


def parse_company_tickers(document: bytes | str, *, as_of: date) -> list[TickerRow]:
    """Parse company_tickers.json into crosswalk rows.

    HONEST LIMITATION, and it is the reason this is a crosswalk and not history:
    the file says which ticker a CIK has **today**. It carries no start date. So
    `valid_from` is the date we OBSERVED the pairing, not the date it began, and
    `valid_to` is NULL because it is current.

    A historical ticker lookup against these rows will therefore return nothing
    before the first observation. That is correct behaviour for data we do not
    have, and it is why ruling 5 keys the universe on CIK. Recovering true
    ticker validity ranges needs a source we do not yet have.
    """
    if isinstance(document, bytes):
        document = document.decode("utf-8")
    d = json.loads(document)
    entries = d.values() if isinstance(d, dict) else d

    rows: list[TickerRow] = []
    for entry in entries:
        cik = parse_entity_identifier(SEC_CIK_SCHEME, str(entry["cik_str"]))
        ticker = (entry.get("ticker") or "").strip().upper()
        if not ticker:
            continue
        rows.append(
            TickerRow(
                cik=cik,
                ticker=ticker,
                exchange=(entry.get("exchange") or None),
                valid_from=as_of,
            )
        )
    return rows


# ---------------------------------------------------------------------------
# Loading. Every statement is ON CONFLICT DO NOTHING against a real constraint.
# ---------------------------------------------------------------------------

def record_fetch(cur, fetch) -> int:
    """Record a retrieval and return its fetch_id.

    Takes an ``ingest.edgar.Fetch`` - the client already produced D-023's three
    required values and, before 0002, had nowhere to put them.

    **Called before the rows it provenances, in the same transaction.** If the
    load fails, the fetch row goes with it. A fetch row without the data it
    produced is merely untidy; data without its fetch row is unprovenanced
    forever, because re-fetching produces a new fetch rather than evidence of
    the old one.

    ``ON CONFLICT DO NOTHING`` on (url, retrieved_at) makes re-recording the
    same retrieval a no-op, so the loader stays idempotent. Note what it does
    **not** collapse: the same URL fetched at a different moment is a different
    event and gets its own row, whether or not the payload changed. That is the
    point of the key.
    """
    cur.execute(
        """
        INSERT INTO fetch_log (url, retrieved_at, sha256, content_bytes)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (url, retrieved_at) DO NOTHING
        RETURNING fetch_id
        """,
        (fetch.url, fetch.retrieved_at, fetch.sha256, len(fetch.body)),
    )
    row = cur.fetchone()
    if row is not None:
        return row[0]
    # DO NOTHING suppresses RETURNING, so this retrieval was already recorded.
    cur.execute(
        "SELECT fetch_id FROM fetch_log WHERE url = %s AND retrieved_at = %s",
        (fetch.url, fetch.retrieved_at),
    )
    return cur.fetchone()[0]


def load_filers(cur, filers, *, fetch_id: int) -> int:
    rows = [(f.cik, f.current_name, f.current_sic, f.current_sic_desc,
             f.metadata_as_of, fetch_id)
            for f in filers]
    if not rows:
        return 0
    cur.executemany(
        """
        INSERT INTO filer (cik, current_name, current_sic, current_sic_desc,
                           metadata_as_of, source_fetch_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (cik) DO NOTHING
        """,
        rows,
    )
    return len(rows)


def load_filings(cur, filings, *, fetch_id: int) -> int:
    rows = [(f.accession, f.cik, f.form_type, f.filing_date,
             f.period_of_report, f.is_amendment, fetch_id)
            for f in filings]
    if not rows:
        return 0
    cur.executemany(
        """
        INSERT INTO filing (accession, cik, form_type, filing_date,
                            period_of_report, is_amendment, sic_at_filing,
                            source_fetch_id)
        VALUES (%s, %s, %s, %s, %s, %s, NULL, %s)
        ON CONFLICT (accession) DO NOTHING
        """,
        rows,
    )
    return len(rows)


def load_tickers(cur, tickers, *, fetch_id: int) -> int:
    rows = [(t.cik, t.ticker, t.exchange, t.valid_from, t.valid_to, fetch_id)
            for t in tickers]
    if not rows:
        return 0
    # Conflict target is filer_ticker_pk (cik, ticker, valid_from). The EXCLUDE
    # constraint cannot serve as one — ON CONFLICT needs a unique index — which
    # is why 0001 carries both.
    cur.executemany(
        """
        INSERT INTO filer_ticker (cik, ticker, exchange, valid_from, valid_to,
                                  source_fetch_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (cik, ticker, valid_from) DO NOTHING
        """,
        rows,
    )
    return len(rows)
