# Planner document register

Planner-side documents, committed on receipt. **This directory is the relay.**
Losses become impossible here rather than merely detectable, which is the whole
reason it exists. Adopted by owner ruling, 2026-09-25.

## How this set was selected

**By exclusion, not by pattern.** Every `*.md` in the source naming this project is
included unless it is Code-authored (`REPORT-Code-*`, `MANIFEST-Code-*`,
`REPORT-C-013-*`).

An include-pattern of `*-Planner-*` was tried first and **silently missed 11
documents** - the seven `RULING-RECORD-*` files, `RULING-P018-*`,
`PLANNER-RESEARCH-*`, `PLANNER-NOTE-r2-*` and `MANIFEST-r2-Planner-*`. That is the
register's own rule arriving again: **count by diff, never by filename pattern.**
Recorded because the next person to extend this directory will reach for a pattern.

Built from **95 source files**, collapsing
**byte-identical duplicates** to **77 documents**.

## The one content conflict

`RULING-RECORD-2026-09-23-...-owner-rulings.md` existed in two differing versions.
**Both are kept.** The canonical name holds the later revision (*twelve ruled*);
the earlier one (*eleven ruled, two pending clarification*) is retained as
`...owner-rulings.superseded-r1.md`.

The later revision carries two owner rulings the earlier lacks - **Altman Z'**
(ruling 11) and **Lynch-style archetypes, option (c)** (ruling 13). Both were
verified present in `decisions.md` before this directory was built, so the register
took the later revision at the time and nothing was lost.

**Resolved explicitly in code, not by sort order** - the arbitrary pick happened to
land on the right file, which is not a method.

## Known missing

**D28, D30 and D32 were never received.** Each is named as the previous manifest by
a delivery that did arrive (D29, D31, D33), so their absence is established rather
than inferred. D33 records D28's and D30's content as carried in D32 and therefore
**not outstanding** - but D32 did not arrive either, so that content is not here and
the re-send request stands.

## Not included

Snapshot archives and patches (`*-keel-scaffold*.zip`,
`*-register-update-*`) stay out of the repository by standing convention.

## Counts

| Date | Documents |
|---|---|
| 2026-09-22 | 13 |
| 2026-09-23 | 36 |
| 2026-09-24 | 16 |
| 2026-09-25 | 12 |
| **Total** | **77** |

| Type | Count |
|---|---|
| HANDOVER | 8 |
| MANIFEST | 30 |
| NOTE | 1 |
| ORDER | 3 |
| RESEARCH | 1 |
| RULING | 29 |
| RULING-RECORD | 5 |

## Documents

| Document | Type | Date | Bytes | sha256 |
|---|---|---|---|---|
| `HANDOVER-Planner-2026-09-22-StockGraderMDK-phase0-cluster.md` | HANDOVER | 2026-09-22 | 8441 | `ec5ccd46fabc1c17` |
| `HANDOVER-Planner-2026-09-23-StockGraderMDK-backup-strategy-restore-drill.md` | HANDOVER | 2026-09-23 | 8517 | `d4203de985c2e379` |
| `HANDOVER-Planner-2026-09-23-StockGraderMDK-ingest-slice-1.md` | HANDOVER | 2026-09-23 | 7749 | `519b845cda766387` |
| `HANDOVER-Planner-2026-09-23-StockGraderMDK-migration-0001-design.md` | HANDOVER | 2026-09-23 | 5250 | `9e47ae88148b3d4d` |
| `HANDOVER-Planner-2026-09-23-StockGraderMDK-phase0-steps5-6.md` | HANDOVER | 2026-09-23 | 8142 | `ef4a2ef88621e3b4` |
| `HANDOVER-Planner-2026-09-24-StockGraderMDK-fact-slice.md` | HANDOVER | 2026-09-24 | 9441 | `d4f4d25d295cb434` |
| `HANDOVER-Planner-2026-09-24-StockGraderMDK-open53-ruled-revised-orders.md` | HANDOVER | 2026-09-24 | 6302 | `0061d5c6ac96942e` |
| `HANDOVER-Planner-2026-09-25-StockGraderMDK-final-block-before-checkpoint.md` | HANDOVER | 2026-09-25 | 3384 | `f1ef6c9e8c444f39` |
| `MANIFEST-Planner-2026-09-23-StockGraderMDK-D10.md` | MANIFEST | 2026-09-23 | 1655 | `7e272da7282733c3` |
| `MANIFEST-Planner-2026-09-23-StockGraderMDK-D11.md` | MANIFEST | 2026-09-23 | 2360 | `0fa674f4f5051680` |
| `MANIFEST-Planner-2026-09-23-StockGraderMDK-D12.md` | MANIFEST | 2026-09-23 | 1413 | `3ca1cc6bc0a8f120` |
| `MANIFEST-Planner-2026-09-23-StockGraderMDK-D13.md` | MANIFEST | 2026-09-23 | 1702 | `ba6f618a2e1e5f6c` |
| `MANIFEST-Planner-2026-09-23-StockGraderMDK-D14.md` | MANIFEST | 2026-09-23 | 1533 | `5cb05620628a4735` |
| `MANIFEST-Planner-2026-09-23-StockGraderMDK-D15.md` | MANIFEST | 2026-09-23 | 1682 | `46ed13ead287176d` |
| `MANIFEST-Planner-2026-09-23-StockGraderMDK-D16.md` | MANIFEST | 2026-09-23 | 1716 | `bfa2c028c1495511` |
| `MANIFEST-Planner-2026-09-23-StockGraderMDK-D3.md` | MANIFEST | 2026-09-23 | 2063 | `528360bcaa07572c` |
| `MANIFEST-Planner-2026-09-23-StockGraderMDK-D4.md` | MANIFEST | 2026-09-23 | 1643 | `074c1d42145bada0` |
| `MANIFEST-Planner-2026-09-23-StockGraderMDK-D5.md` | MANIFEST | 2026-09-23 | 1623 | `1776835f5896e76f` |
| `MANIFEST-Planner-2026-09-23-StockGraderMDK-D6.md` | MANIFEST | 2026-09-23 | 1977 | `5ad4c815ebd39f0f` |
| `MANIFEST-Planner-2026-09-23-StockGraderMDK-D7.md` | MANIFEST | 2026-09-23 | 1502 | `90c905d96d919959` |
| `MANIFEST-Planner-2026-09-23-StockGraderMDK-D8.md` | MANIFEST | 2026-09-23 | 1365 | `977c651eef49b1d5` |
| `MANIFEST-Planner-2026-09-23-StockGraderMDK-D9.md` | MANIFEST | 2026-09-23 | 1300 | `fe33a889df10c2f4` |
| `MANIFEST-Planner-2026-09-23-StockGraderMDK-delivery.md` | MANIFEST | 2026-09-23 | 2746 | `2376b1b57ba24feb` |
| `MANIFEST-Planner-2026-09-24-StockGraderMDK-D17.md` | MANIFEST | 2026-09-24 | 1876 | `0c53ff8474db780c` |
| `MANIFEST-Planner-2026-09-24-StockGraderMDK-D18.md` | MANIFEST | 2026-09-24 | 1273 | `b401d1ff9fa7294e` |
| `MANIFEST-Planner-2026-09-24-StockGraderMDK-D19.md` | MANIFEST | 2026-09-24 | 1880 | `88088b2d115e297c` |
| `MANIFEST-Planner-2026-09-24-StockGraderMDK-D20.md` | MANIFEST | 2026-09-24 | 1700 | `befc1912f3716fb8` |
| `MANIFEST-Planner-2026-09-24-StockGraderMDK-D21.md` | MANIFEST | 2026-09-24 | 2294 | `fe1706ab59e60e44` |
| `MANIFEST-Planner-2026-09-24-StockGraderMDK-D22.md` | MANIFEST | 2026-09-24 | 1533 | `b175ac9e32445440` |
| `MANIFEST-Planner-2026-09-24-StockGraderMDK-D23.md` | MANIFEST | 2026-09-24 | 2126 | `7c35cfb3e4daef55` |
| `MANIFEST-Planner-2026-09-24-StockGraderMDK-D24.md` | MANIFEST | 2026-09-24 | 1959 | `a7ddeaacc694d1c7` |
| `MANIFEST-Planner-2026-09-25-StockGraderMDK-D25.md` | MANIFEST | 2026-09-25 | 2192 | `285cde2fd6e71230` |
| `MANIFEST-Planner-2026-09-25-StockGraderMDK-D26.md` | MANIFEST | 2026-09-25 | 1763 | `3ca78a80fe6afbfe` |
| `MANIFEST-Planner-2026-09-25-StockGraderMDK-D27.md` | MANIFEST | 2026-09-25 | 2247 | `3609c37f000f6db1` |
| `MANIFEST-Planner-2026-09-25-StockGraderMDK-D29.md` | MANIFEST | 2026-09-25 | 1885 | `30103b9c88d7733c` |
| `MANIFEST-Planner-2026-09-25-StockGraderMDK-D31.md` | MANIFEST | 2026-09-25 | 2028 | `59886568f82034f1` |
| `MANIFEST-Planner-2026-09-25-StockGraderMDK-D33.md` | MANIFEST | 2026-09-25 | 2178 | `406922790400579b` |
| `MANIFEST-r2-Planner-2026-09-23-StockGraderMDK-delivery.md` | MANIFEST | 2026-09-23 | 3641 | `e55bb9ccabd9cfbc` |
| `ORDER-Planner-2026-09-22-StockGraderMDK-first-commit-and-PRs.md` | ORDER | 2026-09-22 | 3828 | `2fc9bf30e6feb6bb` |
| `ORDER-Planner-2026-09-22-StockGraderMDK-first-data-slice.md` | ORDER | 2026-09-22 | 10548 | `5f90d61a976a32eb` |
| `ORDER-Planner-2026-09-22-StockGraderMDK-lay-the-keel.md` | ORDER | 2026-09-22 | 6104 | `8e995882dd98591b` |
| `PLANNER-NOTE-r2-2026-09-23-StockGraderMDK-GQS-variable-source-map.md` | NOTE | 2026-09-23 | 11050 | `5f217ae2dd8a2767` |
| `PLANNER-RESEARCH-2026-09-23-StockGraderMDK-open9-open12-open13.md` | RESEARCH | 2026-09-23 | 9682 | `5d4ea789a2bec5f6` |
| `RULING-P018-2026-09-22-StockGraderMDK-OPEN1-closed-PR5-go.md` | RULING | 2026-09-22 | 6005 | `f3f2e3c7e2a2304a` |
| `RULING-Planner-2026-09-22-StockGraderMDK-D008-D010-D020.md` | RULING | 2026-09-22 | 6999 | `962b20fb7226d02a` |
| `RULING-Planner-2026-09-22-StockGraderMDK-D018-D019-statuses.md` | RULING | 2026-09-22 | 4232 | `59a568430eebc531` |
| `RULING-Planner-2026-09-22-StockGraderMDK-D020-visibility.md` | RULING | 2026-09-22 | 4629 | `59af4e5003796e6e` |
| `RULING-Planner-2026-09-22-StockGraderMDK-F004-F005.md` | RULING | 2026-09-22 | 3213 | `9f65734474984c10` |
| `RULING-Planner-2026-09-22-StockGraderMDK-F006.md` | RULING | 2026-09-22 | 3534 | `baccbbada83760df` |
| `RULING-Planner-2026-09-22-StockGraderMDK-F009.md` | RULING | 2026-09-22 | 3297 | `5d08e6fbc6cd5677` |
| `RULING-Planner-2026-09-22-StockGraderMDK-G-vs-B.md` | RULING | 2026-09-22 | 2620 | `9473e46da21e3ede` |
| `RULING-Planner-2026-09-22-StockGraderMDK-post-keel.md` | RULING | 2026-09-22 | 5649 | `ec41a3d08b845ab3` |
| `RULING-Planner-2026-09-23-StockGraderMDK-backup-mechanics-section4-amended.md` | RULING | 2026-09-23 | 8713 | `3f56bc23d72c01b1` |
| `RULING-Planner-2026-09-23-StockGraderMDK-count-corrected-counter-rule.md` | RULING | 2026-09-23 | 4901 | `0568a04ee3d48967` |
| `RULING-Planner-2026-09-23-StockGraderMDK-drill-accepted-p9-roles-question.md` | RULING | 2026-09-23 | 8601 | `efdadcfd63d7a831` |
| `RULING-Planner-2026-09-23-StockGraderMDK-manifest-scheme-and-pr6.md` | RULING | 2026-09-23 | 4484 | `0e78c071a90f16d2` |
| `RULING-Planner-2026-09-23-StockGraderMDK-migration-0001-accepted-open29-open30.md` | RULING | 2026-09-23 | 7527 | `e8a4c699337bcb28` |
| `RULING-Planner-2026-09-23-StockGraderMDK-open24-answered-roles-survived.md` | RULING | 2026-09-23 | 5423 | `4935dfee6c8424a8` |
| `RULING-Planner-2026-09-23-StockGraderMDK-open26-credential-retrievability.md` | RULING | 2026-09-23 | 5442 | `a47d0b24c479cbc8` |
| `RULING-Planner-2026-09-23-StockGraderMDK-open27-order-with-proof-step.md` | RULING | 2026-09-23 | 4918 | `86ca5296f785e0b3` |
| `RULING-Planner-2026-09-23-StockGraderMDK-open31-ruled-p10-open32.md` | RULING | 2026-09-23 | 7069 | `01a918a87c78d112` |
| `RULING-Planner-2026-09-23-StockGraderMDK-p7-settled-p8-context-string.md` | RULING | 2026-09-23 | 6285 | `cd0e983080b1618a` |
| `RULING-Planner-2026-09-23-StockGraderMDK-slice1-accepted-open34-as-0002.md` | RULING | 2026-09-23 | 6745 | `4e8b0b9e20880376` |
| `RULING-Planner-2026-09-24-StockGraderMDK-0002-accepted-open44-open45.md` | RULING | 2026-09-24 | 7262 | `cf424e3afde5184c` |
| `RULING-Planner-2026-09-24-StockGraderMDK-d12-partial-date-convention.md` | RULING | 2026-09-24 | 4266 | `0780d0903d477379` |
| `RULING-Planner-2026-09-24-StockGraderMDK-delisting-eligibility-r1-lost-twice.md` | RULING | 2026-09-24 | 6149 | `2e30e030a3e81a60` |
| `RULING-Planner-2026-09-24-StockGraderMDK-open36-ruled-open39-d12-lost.md` | RULING | 2026-09-24 | 7610 | `9bc8a367689f0cc4` |
| `RULING-Planner-2026-09-24-StockGraderMDK-open54-open55-open53-framed.md` | RULING | 2026-09-24 | 7883 | `beb6b3880fda26c8` |
| `RULING-Planner-2026-09-25-StockGraderMDK-0003-accepted-open59-open60.md` | RULING | 2026-09-25 | 6768 | `75d8016e5e6558aa` |
| `RULING-Planner-2026-09-25-StockGraderMDK-b9-runs-refusal-first.md` | RULING | 2026-09-25 | 4678 | `6f64368b8c7f4247` |
| `RULING-Planner-2026-09-25-StockGraderMDK-cluster-freeze-open56-open57.md` | RULING | 2026-09-25 | 6961 | `e53bcc8232879f1b` |
| `RULING-Planner-2026-09-25-StockGraderMDK-p11-correction-open53-disk.md` | RULING | 2026-09-25 | 7286 | `c6addd2880fbfab0` |
| `RULING-RECORD-2026-09-23-StockGraderMDK-d019-promotion.md` | RULING-RECORD | 2026-09-23 | 3858 | `493404649f845565` |
| `RULING-RECORD-2026-09-23-StockGraderMDK-owner-rulings.md` | RULING-RECORD | 2026-09-23 | 7742 | `78a258f58d7a8552` |
| `RULING-RECORD-2026-09-23-StockGraderMDK-owner-rulings.superseded-r1.md` | RULING-RECORD | 2026-09-23 | 6091 | `c380b0de5f2e25e0` |
| `RULING-RECORD-2026-09-24-StockGraderMDK-open51-coverage-window.md` | RULING-RECORD | 2026-09-24 | 4563 | `3045de849bef4bc8` |
| `RULING-RECORD-2026-09-25-StockGraderMDK-git-relay-serving-path-final-block.md` | RULING-RECORD | 2026-09-25 | 5861 | `eacb6568c165498c` |
