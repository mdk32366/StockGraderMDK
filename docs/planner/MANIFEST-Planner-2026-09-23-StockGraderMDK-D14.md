# DELIVERY MANIFEST — Planner → Code — StockGraderMDK — 2026-09-23 — D14

**Previous manifest:** `MANIFEST-Planner-2026-09-23-StockGraderMDK-D13.md` (D13).
Listed below as continuity. Not counted.

**Count: 2.** **Re-sends in this delivery: none.**

---

## Delivery D14

| # | Document | Issue | Notes |
|---|---|---|---|
| — | `MANIFEST-Planner-2026-09-23-...-D13.md` | D13, previous manifest | continuity entry, not counted |
| 1 | `HANDOVER-Planner-2026-09-23-...-ingest-slice-1.md` | first | Accepts the runner and the OPEN-29 fix. Orders ingest slice 1 — filers and filings, no facts. |
| 2 | `MANIFEST-Planner-2026-09-23-...-D14.md` | first — this document | — |

---

## Cumulative, recomputed

**Planner documents issued 2026-09-23: 33.** Thirty-one through D13, plus this
delivery's two.

**Expected on disk at the Builder after this delivery: 32 distinct.**
Thirty-three issued, minus **#3 of D1**, never delivered and discarded.

Count by diff. One genuine document in that folder ends in ` (1)`.

---

## The item most likely to be misread

§5 of the handover: **do not claim ingest exercises A8.**

If the slice draws from a per-CIK endpoint, `entity_cik` is trivially the CIK
that was requested, the co-registrant case never arises, and a green ingest would
imply a coverage it does not have. A8 and the co-registrant fixture remain the
only evidence for OPEN-29's fix.

This is the same shape as the five instruments in §2 of the handover — a result
that looks like confirmation and is silence.
