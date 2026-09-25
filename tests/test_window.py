"""The coverage window's enumeration (D-023's ruled 45 quarters).

Hermetic. These matter because the fetcher and the loader both derive their work
list from this module -- if it enumerates wrongly, the fetcher downloads the
wrong archives and the loader loads them, and nothing downstream disagrees.
"""

from __future__ import annotations

import pytest

from ingest.window import FIRST, LAST, parse, quarters, url


def test_the_ruled_window_is_45_quarters():
    """The figure the whole sizing analysis rests on. 124.4 GB is 45 x a
    quarter's measured footprint; if this returns 44 or 46, every storage
    number in the register is quoting a different window than the code uses."""
    w = quarters()
    assert len(w) == 45
    assert w[0] == FIRST == "2015q2"
    assert w[-1] == LAST == "2026q2"


def test_it_is_ascending_and_has_no_gaps():
    w = quarters()
    assert w == sorted(w, key=parse)
    for a, b in zip(w, w[1:]):
        ya, qa = parse(a)
        yb, qb = parse(b)
        expected = (ya, qa + 1) if qa < 4 else (ya + 1, 1)
        assert (yb, qb) == expected, f"gap between {a} and {b}"


def test_it_wraps_the_year_at_q4():
    assert quarters("2015q3", "2016q2") == ["2015q3", "2015q4", "2016q1", "2016q2"]


def test_a_single_quarter_window_is_one_quarter():
    assert quarters("2026q2", "2026q2") == ["2026q2"]


def test_a_reversed_window_is_refused_rather_than_returning_empty():
    """An empty list would be loaded as 'nothing to do' and look like success."""
    with pytest.raises(ValueError, match="precedes"):
        quarters("2026q2", "2015q2")


@pytest.mark.parametrize("bad", ["2026", "2026q5", "2026q0", "26q2", "", "2026Q2x"])
def test_malformed_quarters_are_refused(bad):
    with pytest.raises(ValueError, match="not a quarter"):
        parse(bad)


def test_url_refuses_a_malformed_quarter_before_building_one():
    """Otherwise a typo becomes a 404 fetch, which reads as a missing archive
    rather than as a bad input."""
    with pytest.raises(ValueError, match="not a quarter"):
        url("2026q9")


def test_url_shape():
    assert url("2026q2").endswith(
        "/files/dera/data/financial-statement-data-sets/2026q2.zip")
