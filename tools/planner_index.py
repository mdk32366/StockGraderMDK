"""Regenerate docs/planner/INDEX.md from the directory's contents.

INDEX.md is the only navigable route into the Planner archive: GitHub disallows
automated access to /tree/ directory views, so a reader who can only follow links
cannot discover the directory. Every document must therefore be linked from here.

A stale index is indistinguishable from a complete one. This script exists so the
index is regenerated as part of the commit that adds documents, never separately --
a hand-maintained index is a manifest with extra steps.

Usage:
    python tools/planner_index.py           # rewrite INDEX.md
    python tools/planner_index.py --check   # exit 1 if INDEX.md is stale
"""

from __future__ import annotations

import collections
import os
import re
import sys
import urllib.parse

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANNER_DIR = os.path.join(HERE, "docs", "planner")
INDEX = os.path.join(PLANNER_DIR, "INDEX.md")

PREAMBLE = """# Planner document register

Planner-side documents for StockGraderMDK, committed on receipt.
Adopted by owner ruling, 2026-09-25.

**This file is the navigation root.** GitHub disallows automated access to
`/tree/` directory views, so a reader who can only follow links cannot discover
this directory's contents - but every document below is linked from here, and file
pages under `/blob/` are readable. **Any future reorganisation must keep a single
linked index file.** A directory is not a door.

**This file is generated.** Run `python tools/planner_index.py` as part of the same
commit that adds documents; `--check` fails if it is stale. A stale index is
indistinguishable from a complete one, and a hand-maintained one is a manifest with
extra steps.

## What the git relay does and does not fix

An earlier version of this file said losses *"become impossible rather than merely
detectable."* **That was too strong, and it is corrected here** on the Planner's own
correction in D34.

Git is the **archive** and the Planner's **read path**. It is **not** the
Planner -> Code transfer mechanism, which is unchanged.

- **Losses become impossible after receipt.** Before receipt they are exactly as
  possible as on day one - and **every loss so far happened on that hop.**
- **What genuinely improved is verification.** Delivery is confirmed by reading what
  landed rather than by predicting a count and waiting for a mismatch.

## How this set is selected

**By exclusion, not by pattern.** Every `*.md` naming this project is included unless
it is Code-authored (`REPORT-Code-*`, `MANIFEST-Code-*`, `REPORT-C-013-*`).

An include-pattern of `*-Planner-*` was tried first and **silently missed 11
documents**, including all seven `RULING-RECORD-*` files, which carry the owner's own
rulings. It would also have missed `RECOVERY-Planner-*`, a prefix that did not exist
when the pattern was written. **Count by diff, never by filename pattern.**

## Delivery gaps - all closed

**D28, D30 and D32** were never received; each was named as the previous manifest by a
delivery that did arrive. **All three closed on D34**, by content rather than re-send -
re-sending had failed six times.

- **D28** - content carried in `RECOVERY-...-d28-d30-d32-content.md` sections 2-3.
- **D32** - content carried in the same document, section 4.
- **D30** - closed, not outstanding: its unique content arrived by other routes.

**The manifest chain is retired.** D33's end condition was met when the Planner read
this file.

## The one content conflict

`RULING-RECORD-2026-09-23-...-owner-rulings.md` existed in two differing versions.
**Both are kept.** The canonical name holds the later revision (*twelve ruled*); the
earlier (*eleven ruled, two pending*) is retained as `...superseded-r1.md`.

The later revision carries two owner rulings the earlier lacks - **Altman Z-prime**
(ruling 11) and **Lynch-style archetypes, option (c)** (ruling 13). Both were verified
present in `decisions.md` before this directory was built, so the register took the
later revision at the time and nothing was lost. Resolved explicitly in code, not by
sort order.

## Not included

Snapshot archives and patches stay out of the repository by standing convention.
Code-authored reports and manifests are delivered to the owner's Downloads folder.
"""


def classify(name: str) -> str:
    if name.startswith("RULING-RECORD"):
        return "RULING-RECORD"
    if name.startswith("PLANNER-"):
        return name.split("-")[1]
    return name.split("-")[0]


def render() -> str:
    docs = sorted(f for f in os.listdir(PLANNER_DIR) if f.endswith(".md") and f != "INDEX.md")
    rows = []
    for f in docs:
        m = re.search(r"(\d{4}-\d{2}-\d{2})", f)
        rows.append((f, classify(f), m.group(1) if m else "?",
                     os.path.getsize(os.path.join(PLANNER_DIR, f))))

    by_date = collections.Counter(r[2] for r in rows)
    by_type = collections.Counter(r[1] for r in rows)

    out = [PREAMBLE, "\n## Counts\n\n| Date | Documents |\n|---|---|\n"]
    for d in sorted(by_date):
        out.append(f"| {d} | {by_date[d]} |\n")
    out.append(f"| **Total** | **{len(rows)}** |\n\n| Type | Count |\n|---|---|\n")
    for t in sorted(by_type):
        out.append(f"| {t} | {by_type[t]} |\n")

    out.append("\n## Documents\n\nEvery entry links to its file. "
               "This is the only navigable route in.\n")
    for d in sorted(by_date, reverse=True):
        out.append(f"\n### {d}\n\n")
        for name, kind, date, size in rows:
            if date == d:
                out.append(f"- [{name}]({urllib.parse.quote(name)}) - {kind}, {size:,} bytes\n")
    return "".join(out)


def main() -> int:
    new = render()
    check = "--check" in sys.argv
    current = ""
    if os.path.exists(INDEX):
        with open(INDEX, encoding="utf-8") as fh:
            current = fh.read()

    if check:
        if current != new:
            print("INDEX.md is STALE - run: python tools/planner_index.py")
            return 1
        print(f"INDEX.md is current ({new.count(chr(10) + '- [')} documents linked)")
        return 0

    with open(INDEX, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)
    print(f"INDEX.md regenerated: {len([l for l in new.splitlines() if l.startswith('- [')])} documents linked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
