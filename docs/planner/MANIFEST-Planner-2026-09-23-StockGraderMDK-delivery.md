# DELIVERY MANIFEST — Planner → Code — StockGraderMDK — 2026-09-23

**Purpose.** Three relay defects in two days by three distinct mechanisms:
a document lost in both directions (F-020), a cited document that never arrived
(`F-next/relay-loss-recurrence`), and a superseding document reissued under the
same filename (`F-next/same-name-revision`). Sequence numbers catch the first.
Nothing catches the third, because nothing is absent.

**The rule, adopted.** Every Planner delivery is accompanied by a manifest.
The Builder reconciles what arrived against this list **before applying
anything**. A document not on the manifest was not issued by the Planner. A
manifest entry with nothing beside it is a loss, detected at delivery rather
than at citation.

**Revisions get a new filename and say so in the body.** A revision that reuses
its predecessor's name is indistinguishable from a duplicate download, and the
`(1)` suffix the browser adds means the opposite of what it appears to mean.

---

## Documents issued today

| # | Document | Issue | Supersedes |
|---|---|---|---|
| 1 | `HANDOVER-Planner-2026-09-23-...-phase0-steps5-6.md` | first | — |
| 2 | `HANDOVER-Planner-2026-09-23-...-backup-strategy-restore-drill.md` | first | §5 of #1 |
| 3 | `PLANNER-NOTE-2026-09-23-...-GQS-variable-source-map.md` | first | — |
| 4 | `RULING-Planner-2026-09-23-...-backup-mechanics-section4-amended.md` | first (07:19) | §2 B-2/B-6/B-8 and §4 of #2 |
| 5 | `RULING-RECORD-2026-09-23-...-owner-rulings.md` | first (07:29) | — |
| 6 | `RULING-RECORD-2026-09-23-...-owner-rulings.md` | **revision (07:32)** | #5 — **same filename, the defect** |
| 7 | `PLANNER-NOTE-r2-2026-09-23-...-GQS-variable-source-map.md` | **r2** | #3, never delivered |

**Known state at the Builder:** #1, #2, #4, #5, #6 applied. **#3 never
arrived** — reissued as #7, which is complete in itself; #3 needs no
reconciliation and should be discarded if it ever surfaces.

**Entry #6 is recorded as the defect, not corrected out of the record.** It is
the first instance and the reason the rule exists.

---

## Planner error, for the register

**P-4 — the Planner reissued a ruling record under its predecessor's filename
with no supersession marker in the body.** The revision was produced by editing
the delivered document in place. The header's status line changed; nothing else
announced that anything had. The Builder caught it on a 1,651-byte difference in
a directory listing, which is luck.

Rule adopted: **filenames are not identity.** A revised document carries a
revision marker in its filename and a supersession block in its body naming what
it replaces and what changed. The §4-amended ruling (#4) did this correctly and
is the pattern.
