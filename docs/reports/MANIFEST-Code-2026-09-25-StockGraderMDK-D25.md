# DELIVERY MANIFEST — Code → Planner — StockGraderMDK — 2026-09-25 — D25

**Previous manifest:** `MANIFEST-Code-2026-09-25-StockGraderMDK-D24.md` (D24).
Listed below as continuity. Not counted.
If D24 is not in your hands, it is a loss — report it and D25 stands alone.

**Count: 4.** **Re-sends in this delivery: none.**
**Three of the four were delivered earlier today WITHOUT a manifest.** They are
counted here, marked, and explained in §2 of entry 4.

---

## Delivery D25

| # | Document | Issue | Notes |
|---|---|---|---|
| — | `MANIFEST-Code-2026-09-25-...-D24.md` | D24, previous manifest | continuity entry, not counted |
| 1 | `REPORT-Code-2026-09-25-...-fact-loader-built.md` | first | **Delivered earlier with no manifest.** The FSDS fact loader and migration 0004. |
| 2 | `REPORT-Code-2026-09-25-...-segments-grammar-undocumented.md` | first | **Delivered earlier with no manifest.** `readme.htm` does not document the grammar; measuring found a real defect. |
| 3 | `REPORT-Code-2026-09-25-...-first-real-load.md` | first | **Delivered earlier with no manifest.** **3,368,813 facts in a real Fly cluster.** |
| 4 | `REPORT-Code-2026-09-25-...-code-side-manifest-retained.md` | first | The owner ruling this manifest exists because of. **Corrects §7 of entry 1.** |
| 5 | `MANIFEST-Code-2026-09-25-...-D25.md` | first — this document | — |

**On entries 1–3.** They were delivered believing the chain retired. **It was not
retired in this direction**, so they crossed a hand-carried hop with nothing
tracking arrival. **If any of the three is not in your hands, say so and I will
re-send** — that is the sentence that could not be written while no manifest
existed.

---

## Cumulative, recomputed

**Code documents issued: 57** (24 dated 09-23, 15 dated 09-24, 18 dated 09-25).

---

## Reconciliation

**By reading `docs/planner/`, not by arithmetic.** 80 documents present,
matching. No Planner document is outstanding.

**The Planner → Code direction remains sound.** This manifest exists for the
other one.

---

## Headline

**The ruling: the Code-side manifest is retained. The git relay is a worthwhile
improvement that does not yet work in this direction, and a half-working
improvement must not be recorded as a finished one.**

**The error was mine and it is the shape D34 warned about.** §7 of entry 1 argued
that committing Code reports made the retirement symmetric — the Planner reads
`docs/planner/`, so it could read `docs/reports/`. **That depends on the Planner
reaching the repository, and it cannot.** D34's correction said *losses become
impossible after receipt, and every loss so far happened on that hop*; **I
applied it to your direction and assumed mine was safe** because the file also
existed in git. D34 warned specifically against a reader concluding *the relay is
git* and ceasing to watch the live hop. **I was that reader, about my own
direction, in the same sitting.**

**What committing reports is actually for:** a durable archive, so a fresh
Builder context reads a branch instead of sixty files. **Not a delivery
mechanism.**

**What would retire this chain:** you confirming you can read a `docs/reports/`
blob URL — the same standard that met D33's end condition for
`docs/planner/INDEX.md`. **A confirmed read, not an assumption that one would
work.**

**The general form, third instance today:** an improvement that works in one
direction is not symmetric, and **the direction it does not cover keeps the old
failure mode.** A2 enumerated a schema and called it catalogue derivation; A5
tested a proxy and called it the property; this fixed one direction and called it
the relay.

---

## Also in this delivery, and it is the substantive news

**3,368,813 real SEC facts are in `stockgrader_scratch` on the live cluster**, and
**every counter is identical to the local run on a different major version** —
16.15 against 18.3, same bytes, same code, same answer.

**The period derivation is correct on 3.37M rows:** 1,908,661 instants, all
collapsed to a point; 1,460,152 durations, none collapsed. OPEN-41's silent
off-by-one-quarter risk is retired against real data.

**The quarantine caught the case the register itself documented** —
`DerivativeAssetFairValueGrossLiability` holding −3,123,000 and 706,000, both
sides stored.

---

## State at the Builder

**PR-6:** https://github.com/mdk32366/StockGraderMDK/pull/6 — open.
HEAD `44aab39`, **52 commits ahead of main, pushed.** 96/96.

**`stockgrader` untouched. No cluster destroyed. No money spent.** Both
compromised roles still live — OPEN-27 steps 4 and 5 deliberately not started.

**With the owner:** **OPEN-64** (178,555 rows carry no value, including
`NetIncomeLoss` and `StockholdersEquity` — a ruling, not a default) and
**OPEN-65** (~45 min per quarter, ~34 h for 45).

**Next unless redirected:** measure `--defer-indexes` on one quarter. It settles
OPEN-65 for the cost of a single load.

**Blocked:** scoring, on §11.1 / §5.4 — **P-13**. The store now holds real facts
and nothing reads them.
