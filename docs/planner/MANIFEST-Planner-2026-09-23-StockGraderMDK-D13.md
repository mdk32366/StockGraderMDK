# DELIVERY MANIFEST — Planner → Code — StockGraderMDK — 2026-09-23 — D13

**Previous manifest:** `MANIFEST-Planner-2026-09-23-StockGraderMDK-D12.md` (D12).
Listed below as continuity. Not counted.

**Count: 2.** **Re-sends in this delivery: none.**

---

## Delivery D13

| # | Document | Issue | Notes |
|---|---|---|---|
| — | `MANIFEST-Planner-2026-09-23-...-D12.md` | D12, previous manifest | continuity entry, not counted |
| 1 | `RULING-Planner-2026-09-23-...-migration-0001-accepted-open29-open30.md` | first | Accepts 0001. Opens **OPEN-29** (entity in the key) and **OPEN-30** (major-version parity). Rules the runner next. |
| 2 | `MANIFEST-Planner-2026-09-23-...-D13.md` | first — this document | — |

---

## Cumulative, recomputed

**Planner documents issued 2026-09-23: 31.** Twenty-nine through D12, plus this
delivery's two.

**Expected on disk at the Builder after this delivery: 30 distinct.**
Thirty-one issued, minus **#3 of D1**, never delivered and discarded.

**Count by diff, not by filename pattern** — per the rule adopted this delivery.
One genuine document in that folder ends in ` (1)`.

---

## The one item that should be answered before the runner

**OPEN-29.** If the context's entity identifier is not in the uniqueness key,
two co-registrants reporting the same concept for the same period collide, and
`ON CONFLICT DO NOTHING` discards the second while calling it idempotency — a
fact vanishing with no evidence it arrived, which is the failure this schema
exists to refuse.

It may already be handled and simply not listed in the report. If it is not, it
is cheaper now than after any ingest, for the same reason the point-in-time
property was.
