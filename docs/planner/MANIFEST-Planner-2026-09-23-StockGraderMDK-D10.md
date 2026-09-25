# DELIVERY MANIFEST — Planner → Code — StockGraderMDK — 2026-09-23 — D10

**Previous manifest:** `MANIFEST-Planner-2026-09-23-StockGraderMDK-D9.md` (D9).
Listed below as continuity. Not counted.

**Count: 2.** **Re-sends in this delivery: none.**

---

## Delivery D10

| # | Document | Issue | Notes |
|---|---|---|---|
| — | `MANIFEST-Planner-2026-09-23-...-D9.md` | D9, previous manifest | continuity entry, not counted |
| 1 | `RULING-Planner-2026-09-23-...-open24-answered-roles-survived.md` | first | **Voids ruling 6.** Sets a gate on migration 0001's run phase. |
| 2 | `MANIFEST-Planner-2026-09-23-...-D10.md` | first — this document | — |

---

## Cumulative, recomputed

**Planner documents issued 2026-09-23: 25.** Twenty-three through D9, plus this
delivery's two.

**Expected on disk at the Builder after this delivery: 24.**
Twenty-five issued, minus **#3 of D1**, never delivered and discarded.

---

## Register corrections this delivery forces

Three entries assert things that are no longer true and need amending in place
rather than being superseded quietly:

1. **Ruling 6** — void. The destroy retires copies, not originals.
2. **D-029** — has no closure path at present. Say so in those words.
3. **The drill report's §3 claim** that F-017's over-privilege is not rebuilt on
   the clean cluster — there is no clean cluster. Amend with the reason rather
   than deleting the sentence.

**D-031 is untouched and stands.** The app connects as `stockgrader_app` at
`writer`, verified from the connection string's own components. The defect is the
residue the restore carried, not the replacement that was made.
