"""The ruled coverage window, enumerated in one place.

The window is 2015q2..2026q2 - 45 quarters - and it is stated as a ruling, not
derived from today's date. A window that moves when the clock moves would make
every count in the register unreproducible, and *"45 is a starting position, not
a permanent bound"* is a decision to revisit deliberately rather than a default
to drift.

Kept here rather than in a tool so the fetcher and the loader cannot disagree
about what the window is. Two lists that must match are one list.
"""

from __future__ import annotations

import re

FIRST = "2015q2"
LAST = "2026q2"

_QUARTER = re.compile(r"^(\d{4})q([1-4])$")


def parse(q: str) -> tuple[int, int]:
    m = _QUARTER.match(q)
    if not m:
        raise ValueError(f"not a quarter: {q!r} (expected e.g. '2026q2')")
    return int(m.group(1)), int(m.group(2))


def quarters(first: str = FIRST, last: str = LAST) -> list[str]:
    """Inclusive, ascending. 2015q2..2026q2 is 45 quarters."""
    y0, q0 = parse(first)
    y1, q1 = parse(last)
    if (y1, q1) < (y0, q0):
        raise ValueError(f"{last} precedes {first}")
    out: list[str] = []
    y, q = y0, q0
    while (y, q) <= (y1, q1):
        out.append(f"{y}q{q}")
        q += 1
        if q == 5:
            q, y = 1, y + 1
    return out


def url(quarter: str) -> str:
    parse(quarter)  # refuse a malformed quarter before building a URL from it
    return ("https://www.sec.gov/files/dera/data/"
            f"financial-statement-data-sets/{quarter}.zip")
