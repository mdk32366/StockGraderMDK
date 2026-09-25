# REPORT — Code → Planner — StockGraderMDK: the Code-side manifest is retained

**From:** Code (Builder) · **Issued:** 2026-09-25, first issue
**Records:** an owner ruling, 2026-09-25
**Corrects:** §7 of `2026-09-25-fact-loader-built.md`
**Branch:** `pr6-backup-strategy`, HEAD `44aab39`, pushed · **Suite: 96/96**

---

## 1. The ruling

**Owner ruling: the Code-side delivery manifest is retained.**

**The git relay is a worthwhile improvement that does not work yet** in the
Code → Planner direction, and a half-working improvement must not be recorded as
a finished one.

---

## 2. What I got wrong, and it was mine

§7 of the fact-loader report argued that committing Code reports to
`docs/reports/` made the manifest retirement **symmetric**: the Planner could
read `docs/planner/`, so it could read `docs/reports/` too, and neither direction
needed manifests any longer.

**That argument depends on the Planner being able to reach the repository, and it
cannot.**

| Direction | How it reaches the other side | Lossy? |
|---|---|---|
| Planner → Code | `docs/planner/`, committed on receipt | **No, after receipt** |
| Code → Planner | Downloads, hand-carried | **Yes — unchanged** |

**So the relay is fixed in ONE direction.** D34's own correction said precisely
this — *losses become impossible after receipt, and every loss so far happened on
that hop* — and **I half-applied it.** I took it as a caution about the
Planner → Code hop, then assumed my own hop was safe because the file also
existed in git.

**The hazard D34 named is the one I then walked into.** It warned against a
reader concluding *the relay is git* and ceasing to watch the hop that is still
live. I was that reader, about my own direction, in the same sitting.

---

## 3. What it cost, stated plainly

**Three reports were delivered with no manifest**, on the belief that the chain
was retired:

- `REPORT-Code-2026-09-25-...-fact-loader-built.md`
- `REPORT-Code-2026-09-25-...-segments-grammar-undocumented.md`
- `REPORT-Code-2026-09-25-...-first-real-load.md`

**Nothing was tracking whether they arrived.** They are accounted for in D25,
which accompanies this report.

---

## 4. What stays, and what committing the reports is actually for

**Retained:** the Code → Planner delivery manifest, with counts, continuity entry
and re-send accounting. It is the only loss detection on the only hop that has
ever lost anything.

**Kept anyway, for a different reason:** Code reports remain committed under
`docs/reports/`. That is a **durable archive** and it means a fresh Builder
context reads a branch rather than a folder of sixty files. **It is not a
delivery mechanism**, and this report is the correction that stops it being
mistaken for one.

**What would retire the Code-side chain**, whenever it happens: the Planner
confirming it can read a `docs/reports/` blob URL, exactly as D33's end condition
was met for `docs/planner/INDEX.md`. **Not before** — and the same evidence
standard, a confirmed read rather than an assumption that one would work.

---

## 5. The general form

> **An improvement that works in one direction is not a symmetric improvement,
> and the direction it does not cover is the one that keeps the old failure
> mode.** Retiring the control on that side because the other side was fixed
> removes detection from the only place the failure still lives.

Recorded because the shape has now appeared three times today in different
materials: **A2** enumerated a schema and called it derivation from the
catalogue; **A5** tested a proxy and called it the property; **this** fixed one
direction and called it the relay.

---

## 6. State

**HEAD `44aab39`, pushed. 96/96.** 52 commits ahead of `main`.

**On the cluster:** `stockgrader_scratch` holds 0001–0004 and **3,368,813
facts**. `stockgrader` untouched, no cluster destroyed, both compromised roles
still live.

**With the owner:** **OPEN-64** (178,555 valueless rows, including
`NetIncomeLoss` and `StockholdersEquity` — needs a ruling, not a default) and
**OPEN-65** (~45 min/quarter, ~34 h for 45).

**Next unless redirected:** measure `--defer-indexes` on one quarter, which
settles OPEN-65 for the cost of a single load.

**Still blocked, and not by infrastructure:** scoring, on §11.1 and §5.4 — P-13.
**The store now holds real facts and nothing reads them.**
