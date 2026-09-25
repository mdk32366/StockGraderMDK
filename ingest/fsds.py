"""Financial Statement Data Sets — the fact loader.

The ruled fact source (D17 §2, OPEN-36): FSDS quarterly archives, not
companyfacts, because companyfacts carries no dimensions and no per-fact entity
and would discard 60.7% of what filers publish, invisibly.

Everything here follows one rule, stated in the register as `store, don't
filter`: this module's job is to get what the archive says into the store, or to
**refuse and count**. It never silently drops, never defaults a value it could
not parse, and never coerces one thing into a column that means another.

Four refusals are deliberate, each with a register entry behind it:

* **co-registrant facts** (OPEN-39). `coreg` is free text with no reliable path
  to a CIK — 0 of 990 values numeric, 93.8% of carrying submissions have no
  `aciks` at all. `fact.entity_cik` means CIK. So these are refused at ~1.69%
  of rows, as a **chosen refusal we can count**, not an emergent one.
* **unparseable dimensions**. Refused rather than defaulted to `'{}'`, because
  `'{}'` means "no dimensions" and is a different claim from "we could not read
  the dimensions".
* **rows with no value**. `fact.value` is NOT NULL and a fact without one is not
  a fact.
* **collisions that disagree** (OPEN-55). Quarantined into `fact_collision`,
  both competing assertions kept, neither loaded.

**The counts are the product, not a side effect.** `coverage_quarter` carries an
arithmetic constraint that every fact seen was loaded, refused or quarantined,
so a silent drop cannot be recorded as a clean load.
"""

from __future__ import annotations

import calendar
import io
import re
import zipfile
from dataclasses import dataclass
from datetime import date

from .slice1 import IngestError

# ----------------------------------------------------------------------------
# num.txt's documented unique key is
#     (adsh, tag, version, ddate, qtrs, uom, segments, coreg)
# and REAL DATA VIOLATES IT — 2026q2 holds 3,608,711 rows across 3,608,679
# distinct tuples, 32 collisions, and 31 of the 32 carry DIFFERENT VALUES.
#
# So the loader cannot trust the key, and `ON CONFLICT DO NOTHING` against
# 0001's constraint would be silent data loss: keeping one value and discarding
# a genuinely different one, inside the schema built to make that impossible.
# Collisions are detected before insert and quarantined. See F-next/
# fsds-violates-its-own-documented-key.
# ----------------------------------------------------------------------------

_ACCESSION = re.compile(r"^\d{10}-\d{2}-\d{6}$")
_DDATE = re.compile(r"^\d{8}$")

#: The observed `segments` grammar: ``axis=member`` pairs joined by ``;``.
#:
#: This grammar is asserted here rather than inferred silently, and anything not
#: matching it is REFUSED AND COUNTED rather than coerced. That matters more
#: than getting it right first time: if the grammar is wrong, `refused_malformed`
#: in `coverage_quarter` spikes and the coverage row makes it visible. A parser
#: that fell back to `'{}'` would instead record a confident, wrong "no
#: dimensions" for every row it failed to read — which is OPEN-49's shape, a
#: malformed input parsed into something valid.
_SEGMENT_PAIR = re.compile(r"^([^=;]+)=(.*)$", re.S)

#: FSDS marks a filer extension tag by setting `version` equal to `adsh`.
#: Documented in readme.htm, so no heuristic is needed (OPEN-48). Extensions are
#: **counted and reported, never dropped** — they are 7.3%–8.5% of rows and the
#: share is stable across eleven years.


class FactRefused(IngestError):
    """A row we will not load, with the reason attached so it can be counted."""


@dataclass(frozen=True)
class Submission:
    adsh: str
    cik: int
    form: str
    period: date | None
    prevrpt: bool


@dataclass(frozen=True)
class FactRow:
    accession: str
    entity_cik: int
    concept: str
    taxonomy: str
    unit: str
    period_type: str
    period_start: date
    period_end: date
    value: str
    dimensions: dict
    is_extension: bool
    source_ordinal: int

    @property
    def key(self) -> tuple:
        """0001's uniqueness key — what a collision collides on."""
        return (self.accession, self.entity_cik, self.taxonomy, self.concept,
                self.unit, self.period_type, self.period_start, self.period_end,
                _canonical_dimensions(self.dimensions))


def _canonical_dimensions(d: dict) -> str:
    """A stable text form, so two equal dimension sets compare equal in Python.

    Postgres compares `jsonb` semantically; Python dicts compare by content but
    are unhashable. Grouping needs a hashable form that agrees with what the
    database will consider equal, so keys are sorted.
    """
    return ";".join(f"{k}={d[k]}" for k in sorted(d))


def parse_segments(raw: str | None) -> dict:
    """Turn FSDS `segments` into a dimensions mapping, or refuse.

    **The grammar is NOT documented.** `readme.htm` says only *"segments - XBRL
    tags used to represent axis and member reporting"* - no delimiter, no
    format. It was established by measurement against 2,189,835 real values in
    2026q2, and that is recorded here because a reader will otherwise assume it
    came from the specification.

    The shape is ``axis=member`` pairs joined by ``;``, with one complication
    that is FSDS's and not ours: **member values contain bare `amp;`**, the
    wreckage of an HTML entity whose ampersand was stripped during the SEC's own
    extraction. `Dun & Bradstreet` arrives as `Dun amp; Bradstreet`, so the
    delimiter character occurs *inside* values.

    A semicolon therefore only ends a pair when what follows begins another one.
    A fragment with no ``=`` cannot be a new pair, so it is rejoined to the
    previous member. Without that, 12,503 rows per quarter - 0.57% of values
    with dimensions - were refused, concentrated in exactly the filers whose
    holdings carry ampersands in their names.

    The `amp;` is **preserved, not repaired.** `store, don't filter`: what
    arrives is what FSDS asserted, and un-escaping it would be a correction we
    cannot justify per-row. Every value carries the same mangling, so the store
    stays internally consistent and the distortion is recorded rather than
    silently patched.

    Empty means genuinely no dimensions - a real and common state, and the ONLY
    case that yields ``{}``. Anything present but unreadable raises.
    """
    if raw is None:
        return {}
    text = raw.strip()
    if not text:
        return {}

    # Rejoin fragments that cannot be pairs. See the docstring: `;` is both the
    # delimiter and a character occurring inside member values.
    fragments: list[str] = []
    for piece in text.rstrip(";").split(";"):
        if fragments and "=" not in piece:
            fragments[-1] = fragments[-1] + ";" + piece
        else:
            fragments.append(piece)

    out: dict[str, str] = {}
    for part in fragments:
        part = part.strip()
        if not part:
            continue
        m = _SEGMENT_PAIR.match(part)
        if not m:
            raise FactRefused(
                f"segments fragment {part!r} does not match axis=member. "
                "Refused rather than defaulted to '{}': an empty mapping asserts "
                "'no dimensions', which is a different claim from 'unreadable'."
            )
        axis, member = m.group(1).strip(), m.group(2).strip()
        if not axis:
            raise FactRefused(f"segments fragment {part!r} has an empty axis")
        if axis in out and out[axis] != member:
            raise FactRefused(
                f"segments declares axis {axis!r} twice with different members "
                f"({out[axis]!r}, {member!r}); refusing rather than choosing"
            )
        out[axis] = member
    return out


def minus_quarters(d: date, n: int) -> date:
    """Subtract n quarters, clamping to the target month's last day.

    Naive month arithmetic turns 31 March into 31 February. Clamping keeps
    period_start on a real day, and clamping rather than raising is right here
    because the shortened month is a calendar fact, not a data defect.
    """
    month = d.month - 3 * n
    year = d.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    last = calendar.monthrange(year, month)[1]
    return date(year, month, min(d.day, last))


def derive_period(ddate: str, qtrs: str) -> tuple[str, date, date]:
    """`ddate` is the period END; `qtrs` is its duration in quarters.

    Established from readme.htm rather than inferred from samples (OPEN-41),
    and corroborated by distribution: `qtrs=0` is 54.9% of 3.6M rows, which is
    what a balance-sheet-heavy set should look like and what an inverted reading
    would have got badly wrong.

    An off-by-one-quarter error here is silent and poisons every growth metric
    in the TDD's §4.1, which is why it is derived in one place and tested.
    """
    if not _DDATE.match(ddate or ""):
        raise FactRefused(f"ddate {ddate!r} is not YYYYMMDD")
    end = date(int(ddate[0:4]), int(ddate[4:6]), int(ddate[6:8]))
    try:
        n = int(qtrs)
    except (TypeError, ValueError):
        raise FactRefused(f"qtrs {qtrs!r} is not an integer")
    if n < 0:
        raise FactRefused(f"qtrs {qtrs!r} is negative")
    if n == 0:
        # 0001's convention for an instant: period_start = period_end.
        return "instant", end, end
    return "duration", minus_quarters(end, n), end


def classify_taxonomy(version: str, adsh: str) -> tuple[str, bool]:
    """`version = adsh` marks a filer extension tag (OPEN-48, readme.htm)."""
    v = (version or "").strip()
    if not v:
        raise FactRefused("version is empty; cannot tell a standard tag from an extension")
    if v == adsh:
        # Recorded as what it is. The extension's taxonomy IS the filing.
        return v, True
    return v, False


def parse_sub(text: str) -> dict[str, Submission]:
    """Parse `sub.txt` into submissions keyed by accession."""
    out: dict[str, Submission] = {}
    for row in _tsv(text):
        adsh = row.get("adsh", "").strip()
        if not _ACCESSION.match(adsh):
            raise FactRefused(f"sub.txt accession {adsh!r} is not the expected format")
        cik_raw = row.get("cik", "").strip()
        if not cik_raw.isdigit():
            raise FactRefused(f"sub.txt cik {cik_raw!r} for {adsh} is not numeric")
        period = row.get("period", "").strip()
        out[adsh] = Submission(
            adsh=adsh,
            cik=int(cik_raw),
            form=row.get("form", "").strip(),
            period=(date(int(period[0:4]), int(period[4:6]), int(period[6:8]))
                    if _DDATE.match(period) else None),
            # OPEN-40: prevrpt marks the ORIGINAL that was later amended -
            # exactly the value knowable at the time. Stored, NEVER filtered on.
            prevrpt=row.get("prevrpt", "").strip() in ("1", "true", "TRUE"),
        )
    return out


def _tsv(text: str):
    lines = text.splitlines()
    if not lines:
        return
    header = lines[0].split("\t")
    for line in lines[1:]:
        if not line.strip():
            continue
        yield dict(zip(header, line.split("\t")))


@dataclass
class ParseCounts:
    seen: int = 0
    refused_coreg: int = 0
    refused_malformed: int = 0
    extensions: int = 0


def parse_num(text: str, submissions: dict[str, Submission],
              counts: ParseCounts) -> list[FactRow]:
    """Parse `num.txt` into fact rows, refusing and counting as it goes.

    Refusals are returned as counts rather than raised, because one unreadable
    row must not abandon a quarter — but every one is counted, and the coverage
    row will not balance if any goes unrecorded.
    """
    rows: list[FactRow] = []
    for ordinal, r in enumerate(_tsv(text)):
        counts.seen += 1
        adsh = r.get("adsh", "").strip()

        # OPEN-39. Refused as a chosen, countable refusal.
        if (r.get("coreg") or "").strip():
            counts.refused_coreg += 1
            continue

        sub = submissions.get(adsh)
        if sub is None:
            counts.refused_malformed += 1
            continue

        try:
            taxonomy, is_ext = classify_taxonomy(r.get("version", ""), adsh)
            period_type, start, end = derive_period(r.get("ddate", ""),
                                                    r.get("qtrs", ""))
            dims = parse_segments(r.get("segments"))
            value = (r.get("value") or "").strip()
            if not value:
                raise FactRefused("value is empty; fact.value is NOT NULL")
            unit = (r.get("uom") or "").strip()
            if not unit:
                raise FactRefused("uom is empty")
            concept = (r.get("tag") or "").strip()
            if not concept:
                raise FactRefused("tag is empty")
        except FactRefused:
            counts.refused_malformed += 1
            continue

        if is_ext:
            counts.extensions += 1
        rows.append(FactRow(
            accession=adsh, entity_cik=sub.cik, concept=concept,
            taxonomy=taxonomy, unit=unit, period_type=period_type,
            period_start=start, period_end=end, value=value,
            dimensions=dims, is_extension=is_ext, source_ordinal=ordinal,
        ))
    return rows


def partition_collisions(rows: list[FactRow]) -> tuple[list[FactRow], list[FactRow]]:
    """Split rows into (loadable, quarantined).

    A group sharing 0001's key is a collision. If every member agrees on value
    it is an exact duplicate and one row loads. If any member disagrees, **every
    member of the group is quarantined and none loads** — because we cannot tell
    which is right, and choosing would be the silent loss the quarantine exists
    to prevent.

    Note the asymmetry, which is deliberate: agreeing duplicates are cheap to
    collapse and lose nothing; disagreeing ones are the finding.
    """
    groups: dict[tuple, list[FactRow]] = {}
    for row in rows:
        groups.setdefault(row.key, []).append(row)

    loadable: list[FactRow] = []
    quarantined: list[FactRow] = []
    for members in groups.values():
        values = {m.value for m in members}
        if len(values) == 1:
            loadable.append(members[0])
        else:
            quarantined.extend(members)
    return loadable, quarantined


def read_archive(data: bytes) -> tuple[str, str]:
    """Return (sub.txt, num.txt) from an FSDS quarterly zip."""
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = {n.lower(): n for n in z.namelist()}
        for required in ("sub.txt", "num.txt"):
            if required not in names:
                raise FactRefused(
                    f"archive has no {required}; present: {sorted(names)}"
                )
        return (z.read(names["sub.txt"]).decode("utf-8", "replace"),
                z.read(names["num.txt"]).decode("utf-8", "replace"))


# ============================================================================
#  The database side
# ============================================================================

def existing_accessions(cur, accessions) -> set[str]:
    """Which of these accessions are already in `filing`.

    Facts reference `filing`, which is loaded from submissions.zip under ruling
    5. FSDS is a different archive and the two need not agree. A fact whose
    filing is absent is **refused and counted separately** — it is a coverage
    gap between two sources, not malformed input, and inventing the filing row
    to satisfy the foreign key would manufacture a filing we never saw.
    """
    wanted = list({a for a in accessions})
    if not wanted:
        return set()
    cur.execute("SELECT accession FROM filing WHERE accession = ANY(%s)", (wanted,))
    return {r[0] for r in cur.fetchall()}


def load_facts(cur, rows, *, fetch_id: int) -> tuple[int, int]:
    """Insert facts via COPY into a staging table, then one server-side INSERT.

    Returns ``(resolved, newly_inserted)``.

    **Why not executemany.** It issues one round trip per row. Against a local
    cluster that is merely slow (3m09s for a quarter); through `fly mpg proxy`
    to a remote region it is 3.4 MILLION round trips inside a single
    transaction, and on the first real attempt the server closed the connection
    part-way through. The transaction rolled back whole, so nothing was lost -
    but the mechanism cannot carry a quarter, let alone 45.

    COPY streams the same rows in one statement. The conflict handling that
    `ON CONFLICT DO NOTHING` provided is preserved by staging first and then
    inserting server-side, so idempotency is still the schema's property and
    not the loader's.

    **The two return values are different questions and must not be conflated.**
    `resolved` is how many rows THIS LOAD determined were loadable, and it is
    what `coverage_quarter`'s arithmetic must balance against. `newly_inserted`
    is how many rows the database did not already hold. On a first load they
    agree; on a re-ingest the second is 0 while the first is unchanged, which is
    exactly what idempotency looks like from the loader's side.

    `ON CONFLICT DO NOTHING` remains safe HERE and only here, because
    `partition_collisions` has already removed every group whose members
    disagree. Used without that, it is silent data loss.
    """
    if not rows:
        return 0, 0

    cur.execute("""
        CREATE TEMP TABLE _fact_stage (
            accession text, entity_cik bigint, concept text, taxonomy text,
            unit text, period_type text, period_start date, period_end date,
            value text, dimensions text, source_fetch_id bigint
        ) ON COMMIT DROP
    """)
    with cur.copy(
        "COPY _fact_stage (accession, entity_cik, concept, taxonomy, unit, "
        "period_type, period_start, period_end, value, dimensions, "
        "source_fetch_id) FROM STDIN"
    ) as copy:
        for r in rows:
            copy.write_row((r.accession, r.entity_cik, r.concept, r.taxonomy,
                            r.unit, r.period_type, r.period_start, r.period_end,
                            r.value, _json(r.dimensions), fetch_id))

    cur.execute("""
        INSERT INTO fact (accession, entity_cik, concept, taxonomy, unit,
                          period_type, period_start, period_end, value,
                          dimensions, source_fetch_id)
        SELECT accession, entity_cik, concept, taxonomy, unit, period_type,
               period_start, period_end, value::numeric, dimensions::jsonb,
               source_fetch_id
        FROM _fact_stage
        ON CONFLICT ON CONSTRAINT fact_one_per_filing DO NOTHING
    """)
    inserted = cur.rowcount
    cur.execute("DROP TABLE _fact_stage")
    return len(rows), inserted


def quarantine_facts(cur, rows, *, fetch_id: int) -> tuple[int, int]:
    """Record competing assertions. Neither is loaded; both are kept.

    Same COPY-then-insert shape as `load_facts`, for the same reason, and
    returning the same two distinct numbers. OPEN-59's constraint makes the
    insert idempotent across re-ingest.
    """
    if not rows:
        return 0, 0

    cur.execute("""
        CREATE TEMP TABLE _collision_stage (
            accession text, entity_cik bigint, concept text, taxonomy text,
            unit text, period_type text, period_start date, period_end date,
            dimensions text, value text, source_ordinal integer,
            source_fetch_id bigint
        ) ON COMMIT DROP
    """)
    with cur.copy(
        "COPY _collision_stage (accession, entity_cik, concept, taxonomy, unit, "
        "period_type, period_start, period_end, dimensions, value, "
        "source_ordinal, source_fetch_id) FROM STDIN"
    ) as copy:
        for r in rows:
            copy.write_row((r.accession, r.entity_cik, r.concept, r.taxonomy,
                            r.unit, r.period_type, r.period_start, r.period_end,
                            _json(r.dimensions), r.value, r.source_ordinal,
                            fetch_id))

    cur.execute("""
        INSERT INTO fact_collision (accession, entity_cik, concept, taxonomy,
                                    unit, period_type, period_start, period_end,
                                    dimensions, value, source_ordinal,
                                    source_fetch_id)
        SELECT accession, entity_cik, concept, taxonomy, unit, period_type,
               period_start, period_end, dimensions::jsonb, value::numeric,
               source_ordinal, source_fetch_id
        FROM _collision_stage
        ON CONFLICT ON CONSTRAINT fact_collision_one_per_source_row DO NOTHING
    """)
    inserted = cur.rowcount
    cur.execute("DROP TABLE _collision_stage")
    return len(rows), inserted


def record_coverage(cur, *, quarter: str, fetch_id: int, submissions_seen: int,
                    counts: "ParseCounts", facts_loaded: int,
                    refused_unknown_filing: int, collapsed_duplicates: int,
                    quarantined: int) -> None:
    """Write the quarter's coverage row.

    The arithmetic constraint on the table is the real check: if these counters
    do not account for every fact seen, the INSERT is refused and the load fails
    rather than recording a clean-looking partial.
    """
    cur.execute(
        """
        INSERT INTO coverage_quarter (
            quarter, source_fetch_id, submissions_seen, facts_seen,
            facts_loaded, refused_coreg, refused_malformed,
            refused_unknown_filing, collapsed_duplicates, quarantined,
            extension_facts)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (quarter) DO NOTHING
        """,
        (quarter, fetch_id, submissions_seen, counts.seen, facts_loaded,
         counts.refused_coreg, counts.refused_malformed,
         refused_unknown_filing, collapsed_duplicates, quarantined,
         counts.extensions),
    )


def _json(d: dict) -> str:
    import json
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def load_quarter(cur, *, quarter: str, fetch, archive: bytes) -> dict:
    """Load one FSDS quarter. Returns the counters that were recorded.

    Ordering matters and is the same as slice 1's: the fetch is recorded first,
    in the same transaction as the rows it provenances. A fetch row without its
    data is untidy; data without its fetch row is unprovenanced forever.
    """
    from .slice1 import record_fetch

    fetch_id = record_fetch(cur, fetch)
    sub_text, num_text = read_archive(archive)
    submissions = parse_sub(sub_text)

    counts = ParseCounts()
    rows = parse_num(num_text, submissions, counts)

    known = existing_accessions(cur, (r.accession for r in rows))
    unknown = [r for r in rows if r.accession not in known]
    rows = [r for r in rows if r.accession in known]

    loadable, quarantined = partition_collisions(rows)
    # Rows that were neither loaded nor quarantined are exact duplicates that
    # collapsed. Derived rather than counted in the loop, so it cannot drift
    # from what partition_collisions actually did.
    collapsed = len(rows) - len(loadable) - len(quarantined)

    loaded_n, loaded_new = load_facts(cur, loadable, fetch_id=fetch_id)
    quarantined_n, quarantined_new = quarantine_facts(cur, quarantined,
                                                      fetch_id=fetch_id)

    record_coverage(cur, quarter=quarter, fetch_id=fetch_id,
                    submissions_seen=len(submissions), counts=counts,
                    facts_loaded=loaded_n,
                    refused_unknown_filing=len(unknown),
                    collapsed_duplicates=collapsed,
                    quarantined=quarantined_n)

    return {
        "quarter": quarter,
        "submissions_seen": len(submissions),
        "facts_seen": counts.seen,
        "facts_loaded": loaded_n,
        "refused_coreg": counts.refused_coreg,
        "refused_malformed": counts.refused_malformed,
        "refused_unknown_filing": len(unknown),
        "collapsed_duplicates": collapsed,
        "quarantined": quarantined_n,
        # Rows the database did not already hold. Equal to the above on a first
        # load; 0 on a re-ingest, which is what idempotency looks like.
        "newly_inserted_facts": loaded_new,
        "newly_inserted_quarantined": quarantined_new,
        "extension_facts": counts.extensions,
    }
