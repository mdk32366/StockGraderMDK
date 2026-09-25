# DELIVERY MANIFEST — Planner → Code — StockGraderMDK — 2026-09-24 — D24

**Previous manifest:** `MANIFEST-Planner-2026-09-24-StockGraderMDK-D23.md` (D23).
Listed below as continuity. Not counted.

**Count: 2.** **Re-sends in this delivery: none.**

---

## Delivery D24

| # | Document | Issue | Notes |
|---|---|---|---|
| — | `MANIFEST-Planner-2026-09-24-...-D23.md` | D23, previous manifest | continuity entry, not counted |
| 1 | `HANDOVER-Planner-2026-09-24-...-open53-ruled-revised-orders.md` | first | **OPEN-53 ruled**: narrow by concept, tier 1, defer the tier question. Records `F-next/cluster-plan-fee-is-per-cluster` and **amends ruling 6's rationale**. |
| 2 | `MANIFEST-Planner-2026-09-24-...-D24.md` | first — this document | — |

---

## Cumulative, recomputed

**Planner documents issued: 53.** Thirty-seven dated 2026-09-23, sixteen dated
2026-09-24.

**Expected on disk at the Builder after this delivery: 52 distinct.**
- dated 2026-09-23: **36**
- dated 2026-09-24: **16**

Your last count was 46 against an expected 48; D23 carried D21's two as re-sends,
so if D23 and D24 both landed the figure should now be 52. **If D21's re-send
failed again, you will be at 50** — say so, and the next attempt is content
pasted directly rather than a third delivery of the same files.

---

## The item worth reading twice

**§2.** Each MPG cluster carries its own plan fee, and the organisation holds
four ready clusters. **Ruling 6's "holds nothing and costs little" is wrong on
the second half** — the retained `stockgrader-db` is roughly $41 a month, and
the two PharmFoldMDK orphans roughly $38 each plus storage.

That is on the order of **$120 a month of idle spend, which exceeds the entire
cost of the storage decision this delivery rules on.** The ordering of the old
cluster's destroy does not change — it still waits on the ticker load and a
DB-backed endpoint — but the reason it is worth doing promptly does.
