"""Ingest slice 1 — filers, tickers and filings. No facts.

Sources, ruled in D15 (`D-next/ingest-sources`):

    filer, filing   <- submissions.zip   (all filers, full history)
    filer_ticker    <- company_tickers*.json  (current-day crosswalk ONLY)

The ticker files are **not** the universe. Measured 2026-09-23 they hold 8,049
distinct CIKs, every one currently listed — Lehman, Sears, Bed Bath & Beyond and
Enron are all absent. A universe seeded from them cannot contain a company that
stopped trading, which is the survivorship bias ruling 5 exists to close. They
are the identifier crosswalk and nothing else (P-10).

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

def load_filers(cur, filers) -> int:
    rows = [(f.cik, f.current_name, f.current_sic, f.current_sic_desc, f.metadata_as_of)
            for f in filers]
    if not rows:
        return 0
    cur.executemany(
        """
        INSERT INTO filer (cik, current_name, current_sic, current_sic_desc, metadata_as_of)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (cik) DO NOTHING
        """,
        rows,
    )
    return len(rows)


def load_filings(cur, filings) -> int:
    rows = [(f.accession, f.cik, f.form_type, f.filing_date,
             f.period_of_report, f.is_amendment)
            for f in filings]
    if not rows:
        return 0
    cur.executemany(
        """
        INSERT INTO filing (accession, cik, form_type, filing_date,
                            period_of_report, is_amendment, sic_at_filing)
        VALUES (%s, %s, %s, %s, %s, %s, NULL)
        ON CONFLICT (accession) DO NOTHING
        """,
        rows,
    )
    return len(rows)


def load_tickers(cur, tickers) -> int:
    rows = [(t.cik, t.ticker, t.exchange, t.valid_from, t.valid_to) for t in tickers]
    if not rows:
        return 0
    # Conflict target is filer_ticker_pk (cik, ticker, valid_from). The EXCLUDE
    # constraint cannot serve as one — ON CONFLICT needs a unique index — which
    # is why 0001 carries both.
    cur.executemany(
        """
        INSERT INTO filer_ticker (cik, ticker, exchange, valid_from, valid_to)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (cik, ticker, valid_from) DO NOTHING
        """,
        rows,
    )
    return len(rows)
