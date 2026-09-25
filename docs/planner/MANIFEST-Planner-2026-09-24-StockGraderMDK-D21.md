# DELIVERY MANIFEST — Planner → Code — StockGraderMDK — 2026-09-24 — D21

**Previous manifest:** `MANIFEST-Planner-2026-09-24-StockGraderMDK-D20.md` (D20).
Listed below as continuity. Not counted.

**Count: 2.** **Re-sends in this delivery: none.**

---

## Delivery D21

| # | Document | Issue | Notes |
|---|---|---|---|
| — | `MANIFEST-Planner-2026-09-24-...-D20.md` | D20, previous manifest | continuity entry, not counted |
| 1 | `HANDOVER-Planner-2026-09-24-...-fact-slice.md` | first | The fact-slice handover. Opens **OPEN-48, 49, 50, 51**. **§5 needs an owner ruling before building.** |
| 2 | `MANIFEST-Planner-2026-09-24-...-D21.md` | first — this document | — |

---

## Cumulative, recomputed

**Planner documents issued: 47.** Thirty-seven dated 2026-09-23, ten dated
2026-09-24.

**Expected on disk at the Builder after this delivery: 46 distinct.**
- dated 2026-09-23: **36**
- dated 2026-09-24: **10**

Your last count was 44 against an expected 44.

---

## Each source cited against the ruling it satisfies — P-10's rule, applied

| Input | Ruling it satisfies |
|---|---|
| FSDS `num.txt` → `fact` | **OPEN-36**, on the dimensions pillar alone |
| FSDS `sub.txt` → submission metadata, `prevrpt` | **OPEN-40** |
| `ddate` / `qtrs` → period columns | **OPEN-41** |
| `submissions.zip` → `filing` (read only, slice 1 owns it) | **ruling 5**, unchanged |
| `company_tickers*.json` | **not used in this slice** |
| `sub.txt.sic` → `sic_at_filing` | **withheld**, OPEN-37 unanswered |

P-10 was the Planner naming sources without checking them against the rulings
they were supposed to satisfy. This table is the rule it produced, applied to the
document that would otherwise have repeated it.

---

## The item that stops the build

**§5 — sizing.** A full-history load is plausibly over a hundred million fact
rows against a 15 GB disk that arrived by a silent resize.

The measurement is an hour's work. The ruling that follows it is the owner's,
and the order of preference is stated so the choice is made rather than reached:
**narrow by concept, not by dimension** — because FSDS archives are immutable and
re-readable, which makes a narrow ingest reversible, and that asymmetry is what
distinguished this source from the one we rejected.
