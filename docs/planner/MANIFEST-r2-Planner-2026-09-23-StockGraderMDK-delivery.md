# DELIVERY MANIFEST r2 — Planner → Code — StockGraderMDK — 2026-09-23

**Supersedes:** `MANIFEST-Planner-2026-09-23-StockGraderMDK-delivery.md` (first
issue). **What changed:** the manifest now lists itself and its predecessor, and
carries a revision marker in its filename. Nothing else changed.

**Why it changed — `F-next/manifest-omits-itself`.** The first issue listed seven
documents and was itself an eighth. By its own rule — *a document not on the
manifest was not issued by the Planner* — it invalidated itself. It also carried
no revision marker, so a second manifest issued the same day would have reused
its filename: `F-next/same-name-revision` reproduced inside the control written
to prevent it. A guard that does not cover its own artifact has a hole the exact
shape of the artifact.

---

## The rule

Every Planner delivery carries a manifest. The Builder reconciles what arrived
against it **before applying anything**. A manifest entry with nothing beside it
is a loss, detected at delivery rather than at citation. **The manifest lists
itself**, so the delivery is self-describing and a missing manifest is visible
as an absent entry in the next one.

**Filenames are not identity.** A revision gets a revision marker in its
filename and a supersession block in its body naming what it replaces and what
changed. The `(1)` a browser appends means the opposite of what it appears to
mean.

---

## Documents issued 2026-09-23

Issue times are the Builder's observed receipt times where recorded. **"not
recorded" means the Planner did not capture one** — stated rather than left
blank, since a blank reads as an absence of the document rather than of the
timestamp.

| # | Document | Issue | Supersedes |
|---|---|---|---|
| 1 | `HANDOVER-Planner-2026-09-23-...-phase0-steps5-6.md` | first, not recorded | — |
| 2 | `HANDOVER-Planner-2026-09-23-...-backup-strategy-restore-drill.md` | first, not recorded | §5 of #1 |
| 3 | `PLANNER-NOTE-2026-09-23-...-GQS-variable-source-map.md` | first, not recorded | — |
| 4 | `RULING-Planner-2026-09-23-...-backup-mechanics-section4-amended.md` | first, 07:19 | §2 B-2/B-6/B-8 and §4 of #2 |
| 5 | `RULING-RECORD-2026-09-23-...-owner-rulings.md` | first, 07:29 | — |
| 6 | `RULING-RECORD-2026-09-23-...-owner-rulings.md` | **revision, 07:32** | #5 — **same filename, the defect** |
| 7 | `PLANNER-NOTE-r2-2026-09-23-...-GQS-variable-source-map.md` | **r2**, not recorded | #3, never delivered |
| 8 | `MANIFEST-Planner-2026-09-23-...-delivery.md` | first, not recorded | — |
| 9 | `MANIFEST-r2-Planner-2026-09-23-...-delivery.md` | **r2** — this document | #8 |

**Known state at the Builder:** #1, #2, #4, #5, #6 applied. **#3 never arrived**
— reissued as #7, complete in itself; #3 needs no reconciliation and should be
discarded if it surfaces. #7, #8 and #9 delivered together with this manifest.

**Entries #6 and #8 are recorded as defects, not corrected out of the record.**
They are the reasons the two rules above exist.

---

## Planner errors, for the register

**P-4 — a ruling record reissued under its predecessor's filename with no
supersession marker.** Produced by editing the delivered document in place. Only
a status line differed. The Builder caught it on a 1,651-byte difference in a
directory listing, which is luck, not a guard.

**P-5 — the manifest omitted itself.** The control written to catch P-4 was not
subject to the control. Recorded because the pattern matters more than the
instance: a guard's own artifact is the first thing outside its coverage, and it
is where the next failure of this class will appear.
