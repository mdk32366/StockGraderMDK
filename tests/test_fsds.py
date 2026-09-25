"""Hermetic tests for the FSDS fact loader.

No network, no database. Parsing, the period derivation, the refusals and the
collision partition are all testable without either.

The test that matters most is `test_every_fact_is_accounted_for`. The loader's
counters are not diagnostics: `coverage_quarter` carries a CHECK that every fact
seen was loaded, refused or quarantined, so a counter that does not balance
makes the load fail rather than recording a clean-looking partial. That property
is asserted here at the parse layer, where it originates.
"""

from __future__ import annotations

from datetime import date

import pytest

from ingest.fsds import (
    FactRefused,
    ParseCounts,
    classify_taxonomy,
    derive_period,
    minus_quarters,
    parse_num,
    parse_segments,
    parse_sub,
    partition_collisions,
)

ADSH = "0001628280-26-034133"
OTHER = "0000320193-26-000010"

SUB = "\t".join(["adsh", "cik", "name", "form", "period", "prevrpt"]) + "\n" + \
      "\t".join([ADSH, "1628280", "EXAMPLE CORP", "10-Q", "20260331", "0"]) + "\n" + \
      "\t".join([OTHER, "320193", "OTHER INC", "10-K", "20260331", "1"]) + "\n"

NUM_HEADER = "\t".join(
    ["adsh", "tag", "version", "coreg", "ddate", "qtrs", "uom", "segments", "value"])


def num(*rows: list[str]) -> str:
    return NUM_HEADER + "\n" + "\n".join("\t".join(r) for r in rows) + "\n"


# ---------------------------------------------------------------------------
# OPEN-41: ddate is the period END, qtrs the duration. An off-by-one-quarter
# error here is silent and poisons every growth metric.
# ---------------------------------------------------------------------------

def test_qtrs_zero_is_an_instant_and_collapses_to_a_point():
    kind, start, end = derive_period("20260331", "0")
    assert kind == "instant"
    # 0001 CHECKs that an instant has period_start = period_end.
    assert start == end == date(2026, 3, 31)


def test_qtrs_one_is_a_duration_ending_at_ddate():
    kind, start, end = derive_period("20260331", "1")
    assert kind == "duration"
    assert end == date(2026, 3, 31)
    assert start == date(2025, 12, 31)


def test_four_quarters_is_a_year():
    _, start, end = derive_period("20261231", "4")
    assert (start, end) == (date(2025, 12, 31), date(2026, 12, 31))


def test_period_is_never_inverted():
    """0001 CHECKs period_start <= period_end; the deriver must not produce one
    that violates it, for any quarter count."""
    for q in range(0, 21):
        _, start, end = derive_period("20260331", str(q))
        assert start <= end, f"qtrs={q} produced an inverted period"


def test_month_end_is_clamped_not_overflowed():
    # 31 May minus one quarter is 28 February, not an invalid 31 February.
    assert minus_quarters(date(2026, 5, 31), 1) == date(2026, 2, 28)
    assert minus_quarters(date(2024, 5, 31), 1) == date(2024, 2, 29)  # leap


def test_malformed_period_inputs_are_refused_not_guessed():
    for bad in ("2026-03-31", "202603", "", "notadate"):
        with pytest.raises(FactRefused):
            derive_period(bad, "0")
    with pytest.raises(FactRefused):
        derive_period("20260331", "x")
    with pytest.raises(FactRefused):
        derive_period("20260331", "-1")


# ---------------------------------------------------------------------------
# OPEN-48: version = adsh marks a filer extension. Documented, not heuristic.
# ---------------------------------------------------------------------------

def test_version_equal_to_adsh_is_an_extension():
    taxonomy, is_ext = classify_taxonomy(ADSH, ADSH)
    assert is_ext is True
    assert taxonomy == ADSH


def test_standard_tag_is_not_an_extension():
    taxonomy, is_ext = classify_taxonomy("us-gaap/2025", ADSH)
    assert is_ext is False
    assert taxonomy == "us-gaap/2025"


def test_empty_version_is_refused():
    with pytest.raises(FactRefused):
        classify_taxonomy("", ADSH)


# ---------------------------------------------------------------------------
# Dimensions. The rule is refuse, never default to '{}'.
# ---------------------------------------------------------------------------

def test_absent_segments_is_genuinely_no_dimensions():
    assert parse_segments("") == {}
    assert parse_segments(None) == {}


def test_segments_parse_to_axis_member_pairs():
    assert parse_segments("ProductAxis=WidgetMember;RegionAxis=EMEAMember") == {
        "ProductAxis": "WidgetMember",
        "RegionAxis": "EMEAMember",
    }


def test_trailing_semicolon_is_not_an_empty_dimension():
    assert parse_segments("ProductAxis=WidgetMember;") == {"ProductAxis": "WidgetMember"}


def test_unreadable_segments_is_refused_rather_than_emptied():
    """The whole point. '{}' asserts 'no dimensions', which is a DIFFERENT
    claim from 'we could not read the dimensions'. Defaulting would put a
    confident falsehood in the key that 0001 uses for uniqueness."""
    with pytest.raises(FactRefused):
        parse_segments("this is not a pair")


def test_contradictory_axis_is_refused_rather_than_chosen():
    with pytest.raises(FactRefused):
        parse_segments("Axis=A;Axis=B")


def test_repeated_identical_axis_is_harmless():
    assert parse_segments("Axis=A;Axis=A") == {"Axis": "A"}


# ---------------------------------------------------------------------------
# Refusals during the row scan, each one counted.
# ---------------------------------------------------------------------------

def _parse(rows):
    counts = ParseCounts()
    subs = parse_sub(SUB)
    return parse_num(num(*rows), subs, counts), counts


def test_coreg_rows_are_refused_and_counted():
    """OPEN-39: coreg is free text with no reliable path to a CIK, and
    fact.entity_cik means CIK. A chosen refusal we can count."""
    rows, counts = _parse([
        [ADSH, "Revenues", "us-gaap/2025", "", "20260331", "0", "USD", "", "100"],
        [ADSH, "Revenues", "us-gaap/2025", "SUBSIDIARY", "20260331", "0", "USD", "", "200"],
    ])
    assert len(rows) == 1
    assert counts.refused_coreg == 1
    assert counts.seen == 2


def test_a_fact_with_no_value_is_not_a_fact():
    rows, counts = _parse([
        [ADSH, "Revenues", "us-gaap/2025", "", "20260331", "0", "USD", "", ""],
    ])
    assert rows == []
    assert counts.refused_malformed == 1


def test_unknown_submission_is_refused_not_invented():
    rows, counts = _parse([
        ["9999999999-99-999999", "Revenues", "us-gaap/2025", "", "20260331",
         "0", "USD", "", "100"],
    ])
    assert rows == []
    assert counts.refused_malformed == 1


def test_extensions_are_counted_and_still_loaded():
    """7.3%-8.5% of rows. Counted and reported, never dropped."""
    rows, counts = _parse([
        [ADSH, "CustomTag", ADSH, "", "20260331", "0", "USD", "", "100"],
    ])
    assert len(rows) == 1
    assert rows[0].is_extension is True
    assert counts.extensions == 1


def test_entity_cik_comes_from_the_submission_not_the_accession():
    rows, _ = _parse([
        [OTHER, "Revenues", "us-gaap/2025", "", "20260331", "0", "USD", "", "100"],
    ])
    assert rows[0].entity_cik == 320193


# ---------------------------------------------------------------------------
# Collisions. FSDS violates its own documented key: 32 per quarter, 31 of them
# carrying DIFFERENT values.
# ---------------------------------------------------------------------------

def _row(value, ordinal, concept="Revenues"):
    rows, _ = _parse([
        [ADSH, concept, "us-gaap/2025", "", "20260331", "0", "USD", "", value],
    ])
    r = rows[0]
    return type(r)(**{**r.__dict__, "source_ordinal": ordinal})


def test_agreeing_duplicates_collapse_to_one():
    loadable, quarantined = partition_collisions([_row("100", 1), _row("100", 2)])
    assert len(loadable) == 1
    assert quarantined == []


def test_disagreeing_collision_quarantines_every_member_and_loads_none():
    """The failure this prevents: ON CONFLICT DO NOTHING would keep one value
    and discard a genuinely different one, with no record, in the schema built
    to make that impossible."""
    loadable, quarantined = partition_collisions([_row("100", 1), _row("200", 2)])
    assert loadable == []
    assert len(quarantined) == 2
    assert {q.value for q in quarantined} == {"100", "200"}


def test_a_three_way_collision_with_two_agreeing_keeps_all_three():
    """The shape the Planner named: keyed on value alone these collapse to two
    and the archive's second assertion of 200 is silently discarded."""
    loadable, quarantined = partition_collisions(
        [_row("100", 1), _row("200", 2), _row("200", 3)])
    assert loadable == []
    assert len(quarantined) == 3
    assert sorted(q.source_ordinal for q in quarantined) == [1, 2, 3]


def test_different_concepts_do_not_collide():
    loadable, quarantined = partition_collisions(
        [_row("100", 1, "Revenues"), _row("200", 2, "Assets")])
    assert len(loadable) == 2
    assert quarantined == []


def test_dimension_order_does_not_create_a_false_collision():
    """jsonb compares semantically; the Python grouping key must agree with it
    or two identical dimension sets written in different orders would be
    treated as distinct and both inserted, then collide in the database."""
    a = parse_segments("A=1;B=2")
    b = parse_segments("B=2;A=1")
    assert a == b


# ---------------------------------------------------------------------------
# The property the coverage constraint enforces in the database.
# ---------------------------------------------------------------------------

def test_every_fact_is_accounted_for():
    """seen == loadable + refused_coreg + refused_malformed + quarantined.

    coverage_quarter CHECKs this arithmetic, so a loader that dropped a row
    silently could not record a clean load - the INSERT would be refused. This
    asserts the same property where it originates.
    """
    rows, counts = _parse([
        # loads
        [ADSH, "Revenues", "us-gaap/2025", "", "20260331", "0", "USD", "", "100"],
        # extension, also loads
        [ADSH, "CustomTag", ADSH, "", "20260331", "0", "USD", "", "50"],
        # refused: coreg
        [ADSH, "Revenues", "us-gaap/2025", "SUB", "20260331", "0", "USD", "", "1"],
        # refused: no value
        [ADSH, "Assets", "us-gaap/2025", "", "20260331", "0", "USD", "", ""],
        # refused: unreadable dimensions
        [ADSH, "Assets", "us-gaap/2025", "", "20260331", "0", "USD", "junk", "5"],
        # two that disagree -> both quarantined
        [ADSH, "Equity", "us-gaap/2025", "", "20260331", "0", "USD", "", "7"],
        [ADSH, "Equity", "us-gaap/2025", "", "20260331", "0", "USD", "", "9"],
    ])
    loadable, quarantined = partition_collisions(rows)

    assert counts.seen == 7
    assert counts.refused_coreg == 1
    assert counts.refused_malformed == 2
    assert len(quarantined) == 2
    assert len(loadable) == 2

    assert counts.seen == (len(loadable) + counts.refused_coreg
                           + counts.refused_malformed + len(quarantined))


def test_prevrpt_is_recorded_and_not_used_to_filter():
    """OPEN-40: prevrpt marks the ORIGINAL that was later amended - exactly the
    value knowable at the time. Filtering on it would delete the original and
    keep the restatement, implementing the latest-value trap with the SEC's
    assistance."""
    subs = parse_sub(SUB)
    assert subs[OTHER].prevrpt is True
    rows, counts = _parse([
        [OTHER, "Revenues", "us-gaap/2025", "", "20260331", "0", "USD", "", "100"],
    ])
    # The row from an amended submission is still parsed and still loadable.
    assert len(rows) == 1


def test_collapsed_duplicates_are_a_category_not_a_gap():
    """An exact duplicate is neither loaded as its own row, nor refused, nor
    quarantined. Without its own counter it vanishes from the arithmetic.

    This test exists because `coverage_quarter`'s CHECK caught exactly that on
    the loader's first run against a real database: 11 facts seen, 10 accounted
    for. The category was invisible until the constraint refused the row, which
    is the difference between a counter set and an account.
    """
    rows, counts = _parse([
        [ADSH, "Cash", "us-gaap/2025", "", "20260331", "0", "USD", "", "250"],
        [ADSH, "Cash", "us-gaap/2025", "", "20260331", "0", "USD", "", "250"],
        [ADSH, "Revenues", "us-gaap/2025", "", "20260331", "0", "USD", "", "1"],
    ])
    loadable, quarantined = partition_collisions(rows)
    collapsed = len(rows) - len(loadable) - len(quarantined)

    assert len(loadable) == 2      # one Cash, one Revenues
    assert quarantined == []
    assert collapsed == 1          # the second Cash

    assert counts.seen == (len(loadable) + collapsed + len(quarantined)
                           + counts.refused_coreg + counts.refused_malformed)
