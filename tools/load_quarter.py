"""Load one FSDS quarter into the fact store.

    python tools/load_quarter.py --quarter 2026q2 --archive <path-to>.zip

Takes DATABASE_URL from the environment and never writes it anywhere, the same
rule the migration runner follows. Everything happens in ONE transaction: if any
part fails, the fetch row goes with the rows it provenances, because a fetch row
without its data is untidy while data without its fetch row is unprovenanced
forever.

ON THE TWO SOURCES
------------------
`fact` references `filing`, and ruling 5 sources `filer` and `filing` from
`submissions.zip` - all filers, full history, dead companies included. FSDS
`sub.txt` covers only the XBRL submissions in one quarter.

Measured on 2026q2: `num.txt` references 7,714 distinct accessions and `sub.txt`
contains exactly those 7,714, with **zero** orphans. So the two are
complementary rather than competing:

  * `sub.txt` is COMPLETE FOR THE FACTS - every fact's filing is in it, so a
    quarter loaded from FSDS alone is internally consistent.
  * `submissions.zip` remains required for the UNIVERSE - the filings that
    carry no XBRL, the history before the mandate, and the companies that
    stopped filing. That is what OPEN-33's Lehman test is about, and this
    does not substitute for it.

`--submissions` therefore loads filers and filings from `sub.txt` so a quarter
can be loaded standalone. It does not make ruling 5 unnecessary and the rows it
writes carry their own `source_fetch_id`, so which archive produced what stays
answerable.

WHAT IS DELIBERATELY LEFT NULL
------------------------------
Both SIC columns. `sub.txt` carries a per-submission `sic`, but OPEN-37 has not
established whether it means the SIC **as filed** or the filer's SIC **as of
extract** - and which of those it is, is the entire reason `sic_at_filing`
exists. A 97.5% population rate does not say. Until it is established, both stay
honestly NULL rather than confidently wrong.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import zipfile
from datetime import date, datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingest.edgar import Fetch                                    # noqa: E402
from ingest.fsds import load_quarter, parse_sub, read_archive     # noqa: E402

FSDS_URL = "https://www.sec.gov/files/dera/data/financial-statement-data-sets/{q}.zip"

#: `fact`'s QUERY indexes - droppable for a bulk load and rebuilt afterwards.
#:
#: NOT included, and the distinction is the whole point:
#:   * `fact_pkey`            - identity.
#:   * `fact_one_per_filing`  - the ON CONFLICT target. Without it the insert
#:                              has no conflict arbiter and duplicate facts
#:                              become representable, which is the one thing
#:                              0001 exists to prevent. It stays, always.
#:
#: The evidence for building rather than maintaining is OPEN-57's: an index
#: BUILD is cheap - 1,075 MB in 15.4 s even under a 1 GB cgroup - while
#: maintaining seven indexes across 3.4M individual inserts on a 1 GB instance
#: is random I/O per row.
DEFERRABLE = {
    "fact_entity_concept_idx":
        "CREATE INDEX fact_entity_concept_idx ON fact (entity_cik, concept, period_end)",
    "fact_concept_period_idx":
        "CREATE INDEX fact_concept_period_idx ON fact (concept, period_end, period_start)",
    "fact_accession_idx":
        "CREATE INDEX fact_accession_idx ON fact (accession)",
    "fact_source_fetch_idx":
        "CREATE INDEX fact_source_fetch_idx ON fact (source_fetch_id)",
    # PARTIAL. The predicate is not decoration: without it this becomes a
    # different, much larger index that happens to share a name, and nothing
    # would report the substitution.
    "fact_consolidated_idx":
        "CREATE INDEX fact_consolidated_idx ON fact (concept, period_end) "
        "WHERE dimensions = '{}'::jsonb",
}


def _d(raw: str | None) -> date | None:
    raw = (raw or "").strip()
    if len(raw) != 8 or not raw.isdigit():
        return None
    return date(int(raw[:4]), int(raw[4:6]), int(raw[6:8]))


def load_submissions(cur, sub_text: str, *, fetch_id: int, as_of: date) -> tuple[int, int]:
    """Filers and filings from `sub.txt`. See the module docstring on scope."""
    rows = [l.split("\t") for l in sub_text.splitlines() if l.strip()]
    header = rows[0]
    idx = {name: i for i, name in enumerate(header)}
    filers, filings = {}, []
    for r in rows[1:]:
        if len(r) < len(header):
            continue
        cik = r[idx["cik"]].strip()
        if not cik.isdigit():
            continue
        cik = int(cik)
        adsh = r[idx["adsh"]].strip()
        form = r[idx["form"]].strip()
        filers.setdefault(cik, r[idx["name"]].strip())
        filings.append((adsh, cik, form, _d(r[idx["filed"]]),
                        _d(r[idx["period"]]), form.endswith("/A")))

    # COPY, not executemany, for the same reason as the facts: ~14,000 round
    # trips through `fly mpg proxy` is latency paid before the load even reaches
    # the facts. Missed when load_facts was converted - the round-trip argument
    # applies to every insert path over a proxy, not just the largest one.
    cur.execute("CREATE TEMP TABLE _filer_stage (cik bigint, current_name text) "
                "ON COMMIT DROP")
    with cur.copy("COPY _filer_stage (cik, current_name) FROM STDIN") as cp:
        for cik, name in filers.items():
            cp.write_row((cik, name))
    cur.execute(
        """INSERT INTO filer (cik, current_name, current_sic, current_sic_desc,
                              metadata_as_of, source_fetch_id)
           SELECT cik, current_name, NULL, NULL, %s, %s FROM _filer_stage
           ON CONFLICT (cik) DO NOTHING""",
        (as_of, fetch_id))
    cur.execute("DROP TABLE _filer_stage")

    cur.execute("CREATE TEMP TABLE _filing_stage (accession text, cik bigint, "
                "form_type text, filing_date date, period_of_report date, "
                "is_amendment boolean) ON COMMIT DROP")
    with cur.copy("COPY _filing_stage (accession, cik, form_type, filing_date, "
                  "period_of_report, is_amendment) FROM STDIN") as cp:
        for a, c, f, fd, pr, amd in filings:
            if fd is not None:
                cp.write_row((a, c, f, fd, pr, amd))
    cur.execute(
        """INSERT INTO filing (accession, cik, form_type, filing_date,
                               period_of_report, is_amendment, sic_at_filing,
                               source_fetch_id)
           SELECT accession, cik, form_type, filing_date, period_of_report,
                  is_amendment, NULL, %s
           FROM _filing_stage
           ON CONFLICT (accession) DO NOTHING""",
        (fetch_id,))
    cur.execute("DROP TABLE _filing_stage")

    return len(filers), len(filings)


def main() -> int:
    ap = argparse.ArgumentParser(prog="load_quarter")
    ap.add_argument("--quarter", required=True, help="e.g. 2026q2")
    ap.add_argument("--archive", required=True, help="path to the FSDS zip")
    ap.add_argument("--submissions", action="store_true",
                    help="also load filers/filings from sub.txt (see docstring)")
    ap.add_argument("--defer-indexes", action="store_true",
                    help="drop fact's QUERY indexes for the load and rebuild "
                         "them after; see DEFERRED INDEXES in the docstring")
    ap.add_argument("--dry-run", action="store_true",
                    help="parse and report, roll back, write nothing")
    args = ap.parse_args()

    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("DATABASE_URL is not set. This tool takes the DSN from the "
              "environment and never stores it.", file=sys.stderr)
        return 2

    data = open(args.archive, "rb").read()
    sha = hashlib.sha256(data).hexdigest()
    mtime = datetime.fromtimestamp(os.path.getmtime(args.archive), tz=timezone.utc)
    print(f"  archive     : {args.archive}")
    print(f"  bytes       : {len(data):,}")
    print(f"  sha256      : {sha}")
    print(f"  retrieved_at: {mtime.isoformat()}  (file mtime - when it was fetched)")

    fetch = Fetch(url=FSDS_URL.format(q=args.quarter), retrieved_at=mtime,
                  sha256=sha, body=data)

    import psycopg
    with psycopg.connect(dsn, autocommit=False) as conn:
        with conn.cursor() as cur:
            if args.submissions:
                sub_text, _ = read_archive(data)
                cur.execute(
                    """INSERT INTO fetch_log (url, retrieved_at, sha256, content_bytes)
                       VALUES (%s, %s, %s, %s)
                       ON CONFLICT (url, retrieved_at) DO NOTHING
                       RETURNING fetch_id""",
                    (fetch.url, fetch.retrieved_at, fetch.sha256, len(data)))
                row = cur.fetchone()
                if row is None:
                    cur.execute("SELECT fetch_id FROM fetch_log WHERE url=%s "
                                "AND retrieved_at=%s",
                                (fetch.url, fetch.retrieved_at))
                    row = cur.fetchone()
                nf, ng = load_submissions(cur, sub_text, fetch_id=row[0],
                                          as_of=mtime.date())
                print(f"  filers seen : {nf:,}")
                print(f"  filings seen: {ng:,}")

            if args.defer_indexes:
                print("  dropping fact's query indexes for the load")
                for name in DEFERRABLE:
                    cur.execute(f"DROP INDEX IF EXISTS {name}")

            result = load_quarter(cur, quarter=args.quarter, fetch=fetch,
                                  archive=data)

            if args.defer_indexes:
                print("  rebuilding fact's query indexes")
                for name, ddl in DEFERRABLE.items():
                    cur.execute(ddl)

            print("\n=== load ===")
            for k, v in result.items():
                print(f"  {k:>24}: {v if not isinstance(v, int) else format(v, ',')}")

            accounted = (result["facts_loaded"] + result["refused_coreg"]
                         + result["refused_malformed"]
                         + result["refused_unknown_filing"]
                         + result["collapsed_duplicates"] + result["quarantined"])
            print(f"\n  accounted {accounted:,} of {result['facts_seen']:,} seen -> "
                  f"{'BALANCED' if accounted == result['facts_seen'] else 'MISMATCH'}")

            if args.dry_run:
                conn.rollback()
                print("\n  --dry-run: rolled back, nothing written")
                return 0
            conn.commit()
            print("\n  committed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
