# DELIVERY MANIFEST — Planner → Code — StockGraderMDK — 2026-09-25 — D27

**Previous manifest:** `MANIFEST-Planner-2026-09-25-StockGraderMDK-D26.md` (D26).
Listed below as continuity. Not counted.

**Count: 2.** **Re-sends in this delivery: 2** — the whole of D26.

---

## Delivery D27

| # | Document | Issue | Notes |
|---|---|---|---|
| — | `MANIFEST-Planner-2026-09-25-...-D26.md` | D26, previous manifest — **also re-sent below as R1** | continuity entry, not counted |
| R1 | `MANIFEST-Planner-2026-09-25-...-D26.md` | **re-send** | D26's manifest. Unchanged, original filename. |
| R2 | `RULING-Planner-2026-09-25-...-0003-accepted-open59-open60.md` | **re-send** | D26's second document — **0003's review, OPEN-59, OPEN-60, the A4 reframing.** Unchanged. |
| 1 | `RULING-Planner-2026-09-25-...-cluster-freeze-open56-open57.md` | first | **Standing constraint: no cluster is destroyed.** Suspends ruling 6's destroy and B-9. Answers OPEN-56 and redirects OPEN-57. |
| 2 | `MANIFEST-Planner-2026-09-25-...-D27.md` | first — this document | — |

**On the duplicated D26 entry:** it is both this delivery's continuity pointer
and a re-send, because the manifest it points at never arrived. Listed twice
rather than collapsed, so the two roles stay legible.

---

## Cumulative, recomputed

**Planner documents issued: 59.** Thirty-seven dated 2026-09-23, sixteen dated
2026-09-24, six dated 2026-09-25. Re-sends add nothing.

**Expected on disk at the Builder after this delivery: 58 distinct.**
- dated 2026-09-23: **36**
- dated 2026-09-24: **16**
- dated 2026-09-25: **6**

Your last count was 54 against an expected 56 — the shortfall was D26's two.

---

## The item that changes what is already sanctioned

**§1 — no cluster is destroyed.** This suspends **ruling 6's** destroy of
`stockgrader-db` and stops **B-9** from running at all, since its same-sitting
destroy is the condition that makes starting it safe.

**It does not cover OPEN-25's role drops.** Those are operations on roles inside
a living cluster, they remain gated ahead of 0001's run, and their cheap window
still closes when the fact store has tables.

Recorded as a standing constraint rather than a finding, so a handover cannot
miss it.
