# DELIVERY MANIFEST — Planner → Code — StockGraderMDK — 2026-09-25 — D26

**Previous manifest:** `MANIFEST-Planner-2026-09-25-StockGraderMDK-D25.md` (D25).
Listed below as continuity. Not counted.

**Count: 2.** **Re-sends in this delivery: none.**

---

## Delivery D26

| # | Document | Issue | Notes |
|---|---|---|---|
| — | `MANIFEST-Planner-2026-09-25-...-D25.md` | D25, previous manifest | continuity entry, not counted |
| 1 | `RULING-Planner-2026-09-25-...-0003-accepted-open59-open60.md` | first | Accepts 0003. Reframes A4. Opens **OPEN-59** (quarantine idempotency) and **OPEN-60** (A2's schema scope). |
| 2 | `MANIFEST-Planner-2026-09-25-...-D26.md` | first — this document | — |

---

## Cumulative, recomputed

**Planner documents issued: 57.** Thirty-seven dated 2026-09-23, sixteen dated
2026-09-24, four dated 2026-09-25.

**Expected on disk at the Builder after this delivery: 56 distinct.**
- dated 2026-09-23: **36**
- dated 2026-09-24: **16**
- dated 2026-09-25: **4**

---

## The two items, in one line each

**OPEN-59.** Every other insert in this system is idempotent against a real
constraint. `fact_collision` has none by design, so a second load of the same
archive duplicates its own refusal records. **A load that is idempotent
everywhere except in the table recording its refusals is not idempotent.** The
obvious constraint is the wrong one, for the reason you already gave.

**OPEN-60.** A2 derives from the catalogue, and the catalogue query has a scope.
**The inversion moved the enumeration from a table list to a schema — a large
improvement, and still an enumeration.** A table in another schema escapes A2
exactly as `fact` escaped A5.

Neither blocks the measurements. Both come before the fact loader.
