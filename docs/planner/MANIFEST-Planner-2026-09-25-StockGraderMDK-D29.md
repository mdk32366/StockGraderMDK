# DELIVERY MANIFEST — Planner → Code — StockGraderMDK — 2026-09-25 — D29

**Previous manifest:** `MANIFEST-Planner-2026-09-25-StockGraderMDK-D28.md` (D28).
Listed below as continuity. Not counted.

**Count: 2.** **Re-sends in this delivery: none.**

---

## Delivery D29

| # | Document | Issue | Notes |
|---|---|---|---|
| — | `MANIFEST-Planner-2026-09-25-...-D28.md` | D28, previous manifest | continuity entry, not counted |
| 1 | `RULING-Planner-2026-09-25-...-b9-runs-refusal-first.md` | first | **Supersedes §2 of D28's ruling.** B-9 runs, restructured refusal-first. The resulting cluster is retained and recorded. |
| 2 | `MANIFEST-Planner-2026-09-25-...-D29.md` | first — this document | — |

---

## Cumulative, recomputed

**Planner documents issued: 63.** Thirty-seven dated 2026-09-23, sixteen dated
2026-09-24, ten dated 2026-09-25.

**Expected on disk at the Builder after this delivery: 62 distinct.**
- dated 2026-09-23: **36**
- dated 2026-09-24: **16**
- dated 2026-09-25: **10**

---

## The restructuring, in short

B-9 was **create, measure, destroy in one sitting**, and the destroy was what made
it safe to start. **The freeze removes that clause, so the probe is restructured
to make refusals do the work.**

A PITR restore inside the window creates a cluster; one outside it is refused.
**Probe oldest-first on a coarse ladder, every refusal free and every refusal
raising the known lower bound, and stop at the first success.** At most one
cluster is created.

**Two things before the ladder.** A control probe at a timestamp predating the
cluster, which **must** be refused — otherwise the instrument is lying and the
refusals mean nothing. And confirmation that a refusal provisions nothing, by
`fly mpg list` before and after: the structure depends on it, and if a refused
restore leaves a cluster behind that is a finding either way.
