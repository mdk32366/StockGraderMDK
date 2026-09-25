# DELIVERY MANIFEST — Planner → Code — StockGraderMDK — 2026-09-23 — D12

**Previous manifest:** `MANIFEST-Planner-2026-09-23-StockGraderMDK-D11.md` (D11).
Listed below as continuity. Not counted.

**Count: 2.** **Re-sends in this delivery: none.**

---

## Delivery D12

| # | Document | Issue | Notes |
|---|---|---|---|
| — | `MANIFEST-Planner-2026-09-23-...-D11.md` | D11, previous manifest | continuity entry, not counted |
| 1 | `RULING-Planner-2026-09-23-...-open27-order-with-proof-step.md` | first | Amends OPEN-27's order: a proof step between password-setting and the first drop. |
| 2 | `MANIFEST-Planner-2026-09-23-...-D12.md` | first — this document | — |

---

## Cumulative, recomputed

**Planner documents issued 2026-09-23: 29.** Twenty-seven through D11, plus this
delivery's two.

**Expected on disk at the Builder after this delivery: 28.**
Twenty-nine issued, minus **#3 of D1**, never delivered and discarded.

---

## The one thing in this delivery that is not an acceptance

OPEN-27 gains **step 3: prove the new `schema_admin` before dropping anything.**

Created-and-given-a-password is not the same claim as connects-and-runs-DDL, and
the second is the one migration 0001 needs. The proof runs against
`stockgrader_scratch`, which is canary-marked and disposable and is exactly what
it is for.

**Report after step 3.** Step 4 is where the unrecoverable actions start.
