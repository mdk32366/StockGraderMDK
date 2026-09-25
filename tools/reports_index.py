"""Regenerate docs/reports/INDEX.md from the directory's contents.

Same reason as `tools/planner_index.py`, in the other direction. GitHub
disallows automated access to `/tree/` directory views and constructed URLs are
refused, so a reader who can only follow links cannot discover this directory.

**Committed reports with no linked index are durable and unreadable** - the
worst combination, because they look archived. This file is the door.

It is linked from `docs/planner/INDEX.md`, which the Planner can already reach,
so one confirmed read there reaches everything here.

Usage:
    python tools/reports_index.py           # rewrite INDEX.md
    python tools/reports_index.py --check   # exit 1 if stale
"""

from __future__ import annotations

import os
import re
import sys
import urllib.parse

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(HERE, "docs", "reports")
INDEX = os.path.join(REPORTS, "INDEX.md")

PREAMBLE = """# Code reports and manifests

Reports issued by the Builder, committed here as a durable archive.

**This file is the navigation root for this directory**, for the same reason
`docs/planner/INDEX.md` is for that one: directory views are robots-disallowed
and constructed URLs are refused, so a reader who can only follow links needs a
single door. Committed reports with no linked index are durable and unreadable.

## This is an ARCHIVE, not a delivery mechanism

Code reports reach the Planner by being written to the owner's Downloads folder
and hand-carried. **That hop is unchanged and still lossy**, which is why the
Code-side delivery manifest is retained.

An earlier version of this claim got it backwards - it argued that committing
reports made the manifest retirement symmetric. That depends on the Planner
being able to reach this repository, which it cannot yet.

**What would retire the Code-side chain:** the Planner confirming it can read a
blob URL under this directory, the same standard D33 required for
`docs/planner/INDEX.md`. A confirmed read, not an assumption that one would
work.

## The other direction

Planner documents are committed to [`../planner/INDEX.md`](../planner/INDEX.md)
on receipt. That direction is safe after receipt; this one is not.
"""


def title_of(path: str) -> str:
    """The report's own H1, minus the standing prefix."""
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("# "):
                t = line[2:].strip()
                t = re.sub(r"^(REPORT|DELIVERY MANIFEST)\s*[-—]\s*", "", t)
                t = re.sub(r"^Code\s*[-—>→]+\s*(Owner|Planner)[^:]*:\s*", "", t)
                t = re.sub(r"^StockGraderMDK[^:]*:\s*", "", t)
                return t
    return os.path.basename(path)


def render() -> str:
    docs = sorted((f for f in os.listdir(REPORTS)
                   if f.endswith(".md") and f != "INDEX.md"), reverse=True)
    out = [PREAMBLE, f"\n## Documents ({len(docs)})\n\n"
           "Every entry links to its file. This is the only navigable route in.\n\n"]
    for f in docs:
        path = os.path.join(REPORTS, f)
        size = os.path.getsize(path)
        out.append(f"- [{f}]({urllib.parse.quote(f)}) — {title_of(path)} "
                   f"({size:,} bytes)\n")
    return "".join(out)


def main() -> int:
    new = render()
    current = ""
    if os.path.exists(INDEX):
        with open(INDEX, encoding="utf-8") as fh:
            current = fh.read()
    if "--check" in sys.argv:
        if current != new:
            print("docs/reports/INDEX.md is STALE - run: python tools/reports_index.py")
            return 1
        print("docs/reports/INDEX.md is current")
        return 0
    os.makedirs(REPORTS, exist_ok=True)
    with open(INDEX, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)
    n = len([l for l in new.splitlines() if l.startswith("- [")])
    print(f"docs/reports/INDEX.md regenerated: {n} documents linked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
