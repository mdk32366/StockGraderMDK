# DELIVERY MANIFEST — Planner → Code — StockGraderMDK — 2026-09-25 — D33

**Previous manifest:** `MANIFEST-Planner-2026-09-25-StockGraderMDK-D32.md` (D32).
Listed below as continuity. Not counted.

**Count: 2.** **Re-sends in this delivery: none.**

---

## Delivery D33

| # | Document | Issue | Notes |
|---|---|---|---|
| — | `MANIFEST-Planner-2026-09-25-...-D32.md` | D32, previous manifest | continuity entry, not counted |
| 1 | `RULING-RECORD-2026-09-25-...-git-relay-serving-path-final-block.md` | first | **Three owner rulings.** Git relay adopted. OPEN-62 ruled. Final block extended to four items. |
| 2 | `MANIFEST-Planner-2026-09-25-...-D33.md` | first — this document | — |

---

## Cumulative, recomputed

**Planner documents issued: 72.**
**Expected on disk after this delivery: 60 distinct** — your 56, plus D32's two
and this delivery's two. D28's and D30's four remain undelivered and **are not
outstanding**; their content was carried in D32.

---

## The manifest chain's end condition, now that it has one

**Once Planner documents are committed to `docs/planner/` on receipt and the
Planner has confirmed it can read that directory from the public repository, the
chain retires.**

Not before. The last two losses — D28 and D30 — were found by it, and Code's own
draft recommendation to reduce the accounting was disproved in the same sitting
that produced it.

**Verification stops being arithmetic and becomes observation.** The Planner
reads what landed instead of predicting what should have.

---

## The item most likely to be lost if it is not caught now

**§2.3.** "Tracked" means score history, and a score is *for* an as-of date and
*computed at* a moment under a model version.

**Collapsing those is the restatement trap arriving through the output instead of
the input.** If recomputing 2019's score overwrites the row, every backtest
measures today's model against history and nothing says so.

The scores table wants `fact`'s shape — append-only, keyed on the as-of date
**and** the computation, with currency as a query. **It is a constraint on 0004
and it is cheap now and impossible after the first recompute.**
