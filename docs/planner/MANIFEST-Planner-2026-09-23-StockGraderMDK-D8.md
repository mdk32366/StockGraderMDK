# DELIVERY MANIFEST — Planner → Code — StockGraderMDK — 2026-09-23 — D8

**Previous manifest:** `MANIFEST-Planner-2026-09-23-StockGraderMDK-D7.md` (D7).
Listed below as continuity. Not counted.

**Count: 2** — new documents including this manifest, excluding the
carried-forward entry. **Re-sends in this delivery: none.**

---

## Delivery D8

| # | Document | Issue | Notes |
|---|---|---|---|
| — | `MANIFEST-Planner-2026-09-23-...-D7.md` | D7, previous manifest | continuity entry, not counted |
| 1 | `HANDOVER-Planner-2026-09-23-...-migration-0001-design.md` | first | Design-and-review block. Runs now, does not wait on the drill. |
| 2 | `MANIFEST-Planner-2026-09-23-...-D8.md` | first — this document | — |

---

## Cumulative, recomputed

**Planner documents issued 2026-09-23: 21.** Nineteen through D7, plus this
delivery's two.

**Expected on disk at the Builder after this delivery: 20.**
Twenty-one issued, minus **#3 of D1**, never delivered and discarded.

---

## Sequencing note

D8 does not supersede anything and does not change the drill. The drill remains
amended §4, eleven steps, owner at the keyboard, unchanged and waiting.

**Migration 0001 is designed and tested against `stockgrader_scratch` now, and
run against `stockgrader-db-r1` after the cutover.** Those are two blocks, and
the first does not need the second.
