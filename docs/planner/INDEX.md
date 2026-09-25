# Planner document register

Planner-side documents for StockGraderMDK, committed on receipt.
Adopted by owner ruling, 2026-09-25.

**This file is the navigation root.** GitHub disallows automated access to
`/tree/` directory views, so a reader who can only follow links cannot discover
this directory's contents - but every document below is linked from here, and file
pages under `/blob/` are readable. **Any future reorganisation must keep a single
linked index file.** A directory is not a door.

## What the git relay does and does not fix

An earlier version of this file said losses *"become impossible rather than merely
detectable."* **That was too strong, and it is corrected here** on the Planner's
own correction in D34.

Git is the **archive** and the Planner's **read path**. It is **not** the
Planner -> Code transfer mechanism, which is unchanged.

- **Losses become impossible after receipt.** Before receipt they are exactly as
  possible as on day one - and **every loss so far happened on that hop.**
- **What genuinely improved is verification.** Delivery is confirmed by reading
  what landed rather than by predicting a count and waiting for a mismatch. Losses
  stay possible and become immediately visible instead of inferred two deliveries
  later.

The hazard the correction guards against is a reader concluding *the relay is git*
and ceasing to watch the hop that is still live. **The manifest chain therefore
stays** until the Planner confirms it can read this file.

## How this set is selected

**By exclusion, not by pattern.** Every `*.md` naming this project is included
unless it is Code-authored (`REPORT-Code-*`, `MANIFEST-Code-*`, `REPORT-C-013-*`).

An include-pattern of `*-Planner-*` was tried first and **silently missed 11
documents**, including all seven `RULING-RECORD-*` files, which carry the owner's
own rulings. It would also have missed `RECOVERY-Planner-*`, a prefix that did not
exist when the pattern was written. **Count by diff, never by filename pattern.**

## Delivery gaps - all closed

**D28, D30 and D32** were never received; each was named as the previous manifest
by a delivery that did arrive. **All three closed on D34**, by content rather than
re-send - re-sending had failed six times:

- **D28** - content carried in `RECOVERY-...-d28-d30-d32-content.md` sections 2-3.
- **D32** - content carried in the same document, section 4.
- **D30** - closed, not outstanding: its unique content arrived by other routes
  (OPEN-61 in full in D31, OPEN-62 ruled by the owner in D33).

## The one content conflict

`RULING-RECORD-2026-09-23-...-owner-rulings.md` existed in two differing versions.
**Both are kept.** The canonical name holds the later revision (*twelve ruled*);
the earlier (*eleven ruled, two pending*) is retained as `...superseded-r1.md`.

The later revision carries two owner rulings the earlier lacks - **Altman Z'**
(ruling 11) and **Lynch-style archetypes, option (c)** (ruling 13). Both were
verified present in `decisions.md` before this directory was built, so the register
took the later revision at the time and nothing was lost. Resolved explicitly in
code, not by sort order.

## Not included

Snapshot archives and patches (`*-keel-scaffold*.zip`, `*-register-update-*`) stay
out of the repository by standing convention. Code-authored reports and manifests
are delivered to the owner's Downloads folder for the Planner to collect.

## Counts

| Date | Documents |
|---|---|
| 2026-09-22 | 13 |
| 2026-09-23 | 36 |
| 2026-09-24 | 16 |
| 2026-09-25 | 14 |
| **Total** | **79** |

| Type | Count |
|---|---|
| HANDOVER | 8 |
| MANIFEST | 31 |
| NOTE | 1 |
| ORDER | 3 |
| RECOVERY | 1 |
| RESEARCH | 1 |
| RULING | 29 |
| RULING-RECORD | 5 |

## Documents

Every entry links to its file. This is the only navigable route in.


### 2026-09-25

- [HANDOVER-Planner-2026-09-25-StockGraderMDK-final-block-before-checkpoint.md](HANDOVER-Planner-2026-09-25-StockGraderMDK-final-block-before-checkpoint.md) - HANDOVER, 3,384 bytes
- [MANIFEST-Planner-2026-09-25-StockGraderMDK-D25.md](MANIFEST-Planner-2026-09-25-StockGraderMDK-D25.md) - MANIFEST, 2,192 bytes
- [MANIFEST-Planner-2026-09-25-StockGraderMDK-D26.md](MANIFEST-Planner-2026-09-25-StockGraderMDK-D26.md) - MANIFEST, 1,763 bytes
- [MANIFEST-Planner-2026-09-25-StockGraderMDK-D27.md](MANIFEST-Planner-2026-09-25-StockGraderMDK-D27.md) - MANIFEST, 2,247 bytes
- [MANIFEST-Planner-2026-09-25-StockGraderMDK-D29.md](MANIFEST-Planner-2026-09-25-StockGraderMDK-D29.md) - MANIFEST, 1,885 bytes
- [MANIFEST-Planner-2026-09-25-StockGraderMDK-D31.md](MANIFEST-Planner-2026-09-25-StockGraderMDK-D31.md) - MANIFEST, 2,028 bytes
- [MANIFEST-Planner-2026-09-25-StockGraderMDK-D33.md](MANIFEST-Planner-2026-09-25-StockGraderMDK-D33.md) - MANIFEST, 2,178 bytes
- [MANIFEST-Planner-2026-09-25-StockGraderMDK-D34.md](MANIFEST-Planner-2026-09-25-StockGraderMDK-D34.md) - MANIFEST, 2,156 bytes
- [RECOVERY-Planner-2026-09-25-StockGraderMDK-d28-d30-d32-content.md](RECOVERY-Planner-2026-09-25-StockGraderMDK-d28-d30-d32-content.md) - RECOVERY, 7,271 bytes
- [RULING-Planner-2026-09-25-StockGraderMDK-0003-accepted-open59-open60.md](RULING-Planner-2026-09-25-StockGraderMDK-0003-accepted-open59-open60.md) - RULING, 6,768 bytes
- [RULING-Planner-2026-09-25-StockGraderMDK-b9-runs-refusal-first.md](RULING-Planner-2026-09-25-StockGraderMDK-b9-runs-refusal-first.md) - RULING, 4,678 bytes
- [RULING-Planner-2026-09-25-StockGraderMDK-cluster-freeze-open56-open57.md](RULING-Planner-2026-09-25-StockGraderMDK-cluster-freeze-open56-open57.md) - RULING, 6,961 bytes
- [RULING-Planner-2026-09-25-StockGraderMDK-p11-correction-open53-disk.md](RULING-Planner-2026-09-25-StockGraderMDK-p11-correction-open53-disk.md) - RULING, 7,286 bytes
- [RULING-RECORD-2026-09-25-StockGraderMDK-git-relay-serving-path-final-block.md](RULING-RECORD-2026-09-25-StockGraderMDK-git-relay-serving-path-final-block.md) - RULING-RECORD, 5,861 bytes

### 2026-09-24

- [HANDOVER-Planner-2026-09-24-StockGraderMDK-fact-slice.md](HANDOVER-Planner-2026-09-24-StockGraderMDK-fact-slice.md) - HANDOVER, 9,441 bytes
- [HANDOVER-Planner-2026-09-24-StockGraderMDK-open53-ruled-revised-orders.md](HANDOVER-Planner-2026-09-24-StockGraderMDK-open53-ruled-revised-orders.md) - HANDOVER, 6,302 bytes
- [MANIFEST-Planner-2026-09-24-StockGraderMDK-D17.md](MANIFEST-Planner-2026-09-24-StockGraderMDK-D17.md) - MANIFEST, 1,876 bytes
- [MANIFEST-Planner-2026-09-24-StockGraderMDK-D18.md](MANIFEST-Planner-2026-09-24-StockGraderMDK-D18.md) - MANIFEST, 1,273 bytes
- [MANIFEST-Planner-2026-09-24-StockGraderMDK-D19.md](MANIFEST-Planner-2026-09-24-StockGraderMDK-D19.md) - MANIFEST, 1,880 bytes
- [MANIFEST-Planner-2026-09-24-StockGraderMDK-D20.md](MANIFEST-Planner-2026-09-24-StockGraderMDK-D20.md) - MANIFEST, 1,700 bytes
- [MANIFEST-Planner-2026-09-24-StockGraderMDK-D21.md](MANIFEST-Planner-2026-09-24-StockGraderMDK-D21.md) - MANIFEST, 2,294 bytes
- [MANIFEST-Planner-2026-09-24-StockGraderMDK-D22.md](MANIFEST-Planner-2026-09-24-StockGraderMDK-D22.md) - MANIFEST, 1,533 bytes
- [MANIFEST-Planner-2026-09-24-StockGraderMDK-D23.md](MANIFEST-Planner-2026-09-24-StockGraderMDK-D23.md) - MANIFEST, 2,126 bytes
- [MANIFEST-Planner-2026-09-24-StockGraderMDK-D24.md](MANIFEST-Planner-2026-09-24-StockGraderMDK-D24.md) - MANIFEST, 1,959 bytes
- [RULING-Planner-2026-09-24-StockGraderMDK-0002-accepted-open44-open45.md](RULING-Planner-2026-09-24-StockGraderMDK-0002-accepted-open44-open45.md) - RULING, 7,262 bytes
- [RULING-Planner-2026-09-24-StockGraderMDK-d12-partial-date-convention.md](RULING-Planner-2026-09-24-StockGraderMDK-d12-partial-date-convention.md) - RULING, 4,266 bytes
- [RULING-Planner-2026-09-24-StockGraderMDK-delisting-eligibility-r1-lost-twice.md](RULING-Planner-2026-09-24-StockGraderMDK-delisting-eligibility-r1-lost-twice.md) - RULING, 6,149 bytes
- [RULING-Planner-2026-09-24-StockGraderMDK-open36-ruled-open39-d12-lost.md](RULING-Planner-2026-09-24-StockGraderMDK-open36-ruled-open39-d12-lost.md) - RULING, 7,610 bytes
- [RULING-Planner-2026-09-24-StockGraderMDK-open54-open55-open53-framed.md](RULING-Planner-2026-09-24-StockGraderMDK-open54-open55-open53-framed.md) - RULING, 7,883 bytes
- [RULING-RECORD-2026-09-24-StockGraderMDK-open51-coverage-window.md](RULING-RECORD-2026-09-24-StockGraderMDK-open51-coverage-window.md) - RULING-RECORD, 4,563 bytes

### 2026-09-23

- [HANDOVER-Planner-2026-09-23-StockGraderMDK-backup-strategy-restore-drill.md](HANDOVER-Planner-2026-09-23-StockGraderMDK-backup-strategy-restore-drill.md) - HANDOVER, 8,517 bytes
- [HANDOVER-Planner-2026-09-23-StockGraderMDK-ingest-slice-1.md](HANDOVER-Planner-2026-09-23-StockGraderMDK-ingest-slice-1.md) - HANDOVER, 7,749 bytes
- [HANDOVER-Planner-2026-09-23-StockGraderMDK-migration-0001-design.md](HANDOVER-Planner-2026-09-23-StockGraderMDK-migration-0001-design.md) - HANDOVER, 5,250 bytes
- [HANDOVER-Planner-2026-09-23-StockGraderMDK-phase0-steps5-6.md](HANDOVER-Planner-2026-09-23-StockGraderMDK-phase0-steps5-6.md) - HANDOVER, 8,142 bytes
- [MANIFEST-Planner-2026-09-23-StockGraderMDK-D10.md](MANIFEST-Planner-2026-09-23-StockGraderMDK-D10.md) - MANIFEST, 1,655 bytes
- [MANIFEST-Planner-2026-09-23-StockGraderMDK-D11.md](MANIFEST-Planner-2026-09-23-StockGraderMDK-D11.md) - MANIFEST, 2,360 bytes
- [MANIFEST-Planner-2026-09-23-StockGraderMDK-D12.md](MANIFEST-Planner-2026-09-23-StockGraderMDK-D12.md) - MANIFEST, 1,413 bytes
- [MANIFEST-Planner-2026-09-23-StockGraderMDK-D13.md](MANIFEST-Planner-2026-09-23-StockGraderMDK-D13.md) - MANIFEST, 1,702 bytes
- [MANIFEST-Planner-2026-09-23-StockGraderMDK-D14.md](MANIFEST-Planner-2026-09-23-StockGraderMDK-D14.md) - MANIFEST, 1,533 bytes
- [MANIFEST-Planner-2026-09-23-StockGraderMDK-D15.md](MANIFEST-Planner-2026-09-23-StockGraderMDK-D15.md) - MANIFEST, 1,682 bytes
- [MANIFEST-Planner-2026-09-23-StockGraderMDK-D16.md](MANIFEST-Planner-2026-09-23-StockGraderMDK-D16.md) - MANIFEST, 1,716 bytes
- [MANIFEST-Planner-2026-09-23-StockGraderMDK-D3.md](MANIFEST-Planner-2026-09-23-StockGraderMDK-D3.md) - MANIFEST, 2,063 bytes
- [MANIFEST-Planner-2026-09-23-StockGraderMDK-D4.md](MANIFEST-Planner-2026-09-23-StockGraderMDK-D4.md) - MANIFEST, 1,643 bytes
- [MANIFEST-Planner-2026-09-23-StockGraderMDK-D5.md](MANIFEST-Planner-2026-09-23-StockGraderMDK-D5.md) - MANIFEST, 1,623 bytes
- [MANIFEST-Planner-2026-09-23-StockGraderMDK-D6.md](MANIFEST-Planner-2026-09-23-StockGraderMDK-D6.md) - MANIFEST, 1,977 bytes
- [MANIFEST-Planner-2026-09-23-StockGraderMDK-D7.md](MANIFEST-Planner-2026-09-23-StockGraderMDK-D7.md) - MANIFEST, 1,502 bytes
- [MANIFEST-Planner-2026-09-23-StockGraderMDK-D8.md](MANIFEST-Planner-2026-09-23-StockGraderMDK-D8.md) - MANIFEST, 1,365 bytes
- [MANIFEST-Planner-2026-09-23-StockGraderMDK-D9.md](MANIFEST-Planner-2026-09-23-StockGraderMDK-D9.md) - MANIFEST, 1,300 bytes
- [MANIFEST-Planner-2026-09-23-StockGraderMDK-delivery.md](MANIFEST-Planner-2026-09-23-StockGraderMDK-delivery.md) - MANIFEST, 2,746 bytes
- [MANIFEST-r2-Planner-2026-09-23-StockGraderMDK-delivery.md](MANIFEST-r2-Planner-2026-09-23-StockGraderMDK-delivery.md) - MANIFEST, 3,641 bytes
- [PLANNER-NOTE-r2-2026-09-23-StockGraderMDK-GQS-variable-source-map.md](PLANNER-NOTE-r2-2026-09-23-StockGraderMDK-GQS-variable-source-map.md) - NOTE, 11,050 bytes
- [PLANNER-RESEARCH-2026-09-23-StockGraderMDK-open9-open12-open13.md](PLANNER-RESEARCH-2026-09-23-StockGraderMDK-open9-open12-open13.md) - RESEARCH, 9,682 bytes
- [RULING-Planner-2026-09-23-StockGraderMDK-backup-mechanics-section4-amended.md](RULING-Planner-2026-09-23-StockGraderMDK-backup-mechanics-section4-amended.md) - RULING, 8,713 bytes
- [RULING-Planner-2026-09-23-StockGraderMDK-count-corrected-counter-rule.md](RULING-Planner-2026-09-23-StockGraderMDK-count-corrected-counter-rule.md) - RULING, 4,901 bytes
- [RULING-Planner-2026-09-23-StockGraderMDK-drill-accepted-p9-roles-question.md](RULING-Planner-2026-09-23-StockGraderMDK-drill-accepted-p9-roles-question.md) - RULING, 8,601 bytes
- [RULING-Planner-2026-09-23-StockGraderMDK-manifest-scheme-and-pr6.md](RULING-Planner-2026-09-23-StockGraderMDK-manifest-scheme-and-pr6.md) - RULING, 4,484 bytes
- [RULING-Planner-2026-09-23-StockGraderMDK-migration-0001-accepted-open29-open30.md](RULING-Planner-2026-09-23-StockGraderMDK-migration-0001-accepted-open29-open30.md) - RULING, 7,527 bytes
- [RULING-Planner-2026-09-23-StockGraderMDK-open24-answered-roles-survived.md](RULING-Planner-2026-09-23-StockGraderMDK-open24-answered-roles-survived.md) - RULING, 5,423 bytes
- [RULING-Planner-2026-09-23-StockGraderMDK-open26-credential-retrievability.md](RULING-Planner-2026-09-23-StockGraderMDK-open26-credential-retrievability.md) - RULING, 5,442 bytes
- [RULING-Planner-2026-09-23-StockGraderMDK-open27-order-with-proof-step.md](RULING-Planner-2026-09-23-StockGraderMDK-open27-order-with-proof-step.md) - RULING, 4,918 bytes
- [RULING-Planner-2026-09-23-StockGraderMDK-open31-ruled-p10-open32.md](RULING-Planner-2026-09-23-StockGraderMDK-open31-ruled-p10-open32.md) - RULING, 7,069 bytes
- [RULING-Planner-2026-09-23-StockGraderMDK-p7-settled-p8-context-string.md](RULING-Planner-2026-09-23-StockGraderMDK-p7-settled-p8-context-string.md) - RULING, 6,285 bytes
- [RULING-Planner-2026-09-23-StockGraderMDK-slice1-accepted-open34-as-0002.md](RULING-Planner-2026-09-23-StockGraderMDK-slice1-accepted-open34-as-0002.md) - RULING, 6,745 bytes
- [RULING-RECORD-2026-09-23-StockGraderMDK-d019-promotion.md](RULING-RECORD-2026-09-23-StockGraderMDK-d019-promotion.md) - RULING-RECORD, 3,858 bytes
- [RULING-RECORD-2026-09-23-StockGraderMDK-owner-rulings.md](RULING-RECORD-2026-09-23-StockGraderMDK-owner-rulings.md) - RULING-RECORD, 7,742 bytes
- [RULING-RECORD-2026-09-23-StockGraderMDK-owner-rulings.superseded-r1.md](RULING-RECORD-2026-09-23-StockGraderMDK-owner-rulings.superseded-r1.md) - RULING-RECORD, 6,091 bytes

### 2026-09-22

- [HANDOVER-Planner-2026-09-22-StockGraderMDK-phase0-cluster.md](HANDOVER-Planner-2026-09-22-StockGraderMDK-phase0-cluster.md) - HANDOVER, 8,441 bytes
- [ORDER-Planner-2026-09-22-StockGraderMDK-first-commit-and-PRs.md](ORDER-Planner-2026-09-22-StockGraderMDK-first-commit-and-PRs.md) - ORDER, 3,828 bytes
- [ORDER-Planner-2026-09-22-StockGraderMDK-first-data-slice.md](ORDER-Planner-2026-09-22-StockGraderMDK-first-data-slice.md) - ORDER, 10,548 bytes
- [ORDER-Planner-2026-09-22-StockGraderMDK-lay-the-keel.md](ORDER-Planner-2026-09-22-StockGraderMDK-lay-the-keel.md) - ORDER, 6,104 bytes
- [RULING-P018-2026-09-22-StockGraderMDK-OPEN1-closed-PR5-go.md](RULING-P018-2026-09-22-StockGraderMDK-OPEN1-closed-PR5-go.md) - RULING, 6,005 bytes
- [RULING-Planner-2026-09-22-StockGraderMDK-D008-D010-D020.md](RULING-Planner-2026-09-22-StockGraderMDK-D008-D010-D020.md) - RULING, 6,999 bytes
- [RULING-Planner-2026-09-22-StockGraderMDK-D018-D019-statuses.md](RULING-Planner-2026-09-22-StockGraderMDK-D018-D019-statuses.md) - RULING, 4,232 bytes
- [RULING-Planner-2026-09-22-StockGraderMDK-D020-visibility.md](RULING-Planner-2026-09-22-StockGraderMDK-D020-visibility.md) - RULING, 4,629 bytes
- [RULING-Planner-2026-09-22-StockGraderMDK-F004-F005.md](RULING-Planner-2026-09-22-StockGraderMDK-F004-F005.md) - RULING, 3,213 bytes
- [RULING-Planner-2026-09-22-StockGraderMDK-F006.md](RULING-Planner-2026-09-22-StockGraderMDK-F006.md) - RULING, 3,534 bytes
- [RULING-Planner-2026-09-22-StockGraderMDK-F009.md](RULING-Planner-2026-09-22-StockGraderMDK-F009.md) - RULING, 3,297 bytes
- [RULING-Planner-2026-09-22-StockGraderMDK-G-vs-B.md](RULING-Planner-2026-09-22-StockGraderMDK-G-vs-B.md) - RULING, 2,620 bytes
- [RULING-Planner-2026-09-22-StockGraderMDK-post-keel.md](RULING-Planner-2026-09-22-StockGraderMDK-post-keel.md) - RULING, 5,649 bytes
