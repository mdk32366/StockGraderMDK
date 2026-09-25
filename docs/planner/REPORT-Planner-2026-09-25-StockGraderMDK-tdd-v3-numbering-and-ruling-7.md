# REPORT — Planner → Code — StockGraderMDK: the TDD the register gates is not the TDD we hold

**From:** Planner (fresh context, first sitting) · **Issued:** 2026-09-25, first issue
**Read against:** snapshot `SNAPSHOT-StockGraderMDK-2026-09-25-main-bae9729.zip`,
branch `main`, HEAD `bae9729`, suite 98/98
**New artifacts this sitting:** `TDD-growth-score-v3.md` and
`growth-model-lineage.md`, supplied by the owner 2026-09-25. **Neither was in the
repository.**

**For reconciliation with Code.** Nothing here is an order. Every item is either a
finding with its artifact named, or a proposed register change for the owner to
rule and the Builder to apply.

---

## 0. The claim in one paragraph

The register gates the scoring build on a completeness gate it calls **§13**,
which turns on **four open questions in §11**. The document the owner handed me
today — `TDD-growth-score-v3.md`, the document D-010 names by version — has its
completeness gate at **§19** and **five** open questions at **§17**. The mapping
between the two numbering schemes is exact and recoverable for four of the five
questions. **The fifth has no counterpart in the register at all**, it is one of
only two the TDD triages as result-changing, and it is the only open question in
the project with a deadline attached.

**Ruling 7 is the proximate cause, and it runs backwards.** It corrected a
reference that was right into one that is wrong.

---

## 1. What I actually checked

| Artifact | What I read |
|---|---|
| `TDD-growth-score-v3.md` | Header, full heading list, §5, §7, §9.3, §13, §17, §18, §19 in full |
| `growth-model-lineage.md` | Heading list, §8 and its *Carried into the model* block in full |
| `docs/decisions.md` | D-010 in full; rulings 7, 9, 10, 11, 12, 13 |
| `docs/findings.md` | `F-next/gqs-tdd-defects` (F-A through F-D) in full |
| `docs/testplan.md` | The §13 gate-state table; OPEN-63 |
| `docs/gqs-source-map.md` | In full |
| `docs/reports/2026-09-25-first-real-load.md` | §1–§3 |

**Sample:** 2 new documents, 1 full reading each of the sections listed; 1
snapshot. **Heading list extracted programmatically**, not read off by eye — the
crosswalk in §2 is a machine-generated heading dump compared against the
register's own references, which is why I trust it further than I would trust my
own skim.

---

## 2. The crosswalk

The register's numbering is internally consistent and consistently offset. It is
not garbled; it is **a different edition.**

| Register / lineage says | v3 has | Confidence |
|---|---|---|
| §11 — open questions, four of them | **§17 — open questions, five of them** | Exact. v3 §11 is `insufficient_data` and has no numbered subsections |
| §11.1 R&D capitalization | **§17.1** R&D capitalization and useful life | Exact, same text |
| §11.2 sector granularity | **§17.2** | Exact — ruling 13 |
| §11.3 WACC | **§17.3** | Exact — ruling 9 |
| §11.4 size tilt | **§17.4** | Exact — ruling 10 |
| *(nothing)* | **§17.5** price source and split adjustment | **No counterpart in the register** |
| §5.4 R&D treatment | **§13** R&D capitalization — the intangibles adjustment | v3 §5.4 is *Tag resolution* |
| §13 completeness gate | **§19** Completeness gate | Exact |
| §4.1–§4.5 blocks | **§7.1–§7.4** plus **§9** integrity gate | Weights match exactly: 0.30 / 0.30 / 0.25 / 0.15 |
| §12 confirm-before-build | **§18** | Exact, same checklist |
| §5.1 point-in-time | **§5.2** | v3 §5.1 is *two sources, not one* |
| §3 non-goals | §3 non-goals | Unchanged |

**Where the §5.4 pointer came from.** Not from the TDD. `growth-model-lineage.md`
§8 still reads *"R&D capitalization is specified in `TDD-growth-score.md` §5.4."*
**Lineage was never renumbered when the TDD was**, and v3's own change log
(entry 12) records that the v3 assembly retargeted lineage cross-references
indiscriminately and that the defect was caught by the §18 verification pass
rather than by reading. **The stale pointer is a known, documented residue** —
and the register inherited it as though it were current.

---

## 3. `F-A` runs backwards

The register's finding:

> **F-A — D-010's condition cited a section that does not exist.** The ruling said
> *"five open questions in its §17."* The TDD's header says **four** open
> questions in **§11**, and §11 contains exactly four.

`TDD-growth-score-v3.md`, line 4, verbatim scope:

> Five open questions in §17 require owner ratification before a build order;
> §17.0 triages which of them change results.

**D-010 as originally written was correct.** Ruling 7 reworded it to *"the four
open questions in its §11,"* on the stated grounds that it *"now points at a
section that exists."* Against v3 it points at `insufficient_data`.

**My reading, and it is reversible in one line:** the Planner read a pre-v3 file
while D-010 named v3, and nobody compared the header against the document. The
four questions the Planner enumerated — R&D, sector, WACC, size tilt — are
exactly v3's §17.1 through §17.4. **§17.5 is flagged in v3's change log as *new
in v2*.** A four-question §11 is therefore consistent with a **v1** edition, or
with a v2 whose renumber was incomplete. Which file was on disk on 2026-09-23 is
the one thing in this report I cannot establish from here, and §7 asks for it.

**Doctrine this belongs to, already in the error record:** *identifiers a platform
reports are read from the platform, by query.* The same rule covers a document's
own section numbers. A section reference is read from the document, not from a
prior reference to it — and the register's version of the rule was written about
a CI check name, which is why it did not fire here. That is the meta-rule in both
closeouts: **a rule is indexed by the situation that produced it.**

---

## 4. What it costs — the gate is short one result-changing question

v3 §17.0 triages the five. **Two change results:**

| # | Question | Class | v3's stated consequence |
|---|---|---|---|
| **17.1** | R&D useful life | Changes results | Silently reorders every research-intensive company |
| **17.5** | Price source and split adjustment | **Changes results, and has a deadline** | Backtest validity; option (b) only works if daily capture starts now |
| 17.2 | Sector granularity | Mixed | Wrong in a knowable direction, not backwards |
| 17.3 | WACC | Plumbing under the default | Costs a component's contribution, not correctness |
| 17.4 | Size tilt | Preference | Reversible via the settings overlay |

`testplan.md` records: *"§11.1 is now the only open §11 question."* **There are
two open, and the register is tracking one.**

### 4.1 §17.5 is not OPEN-9

This distinction is the substance of the finding, so it is worth stating flatly.

| | OPEN-9 | §17.5 |
|---|---|---|
| Question | **Which vendor** | **How retroactive adjustment is handled** |
| Blocked by | Three properties needing vendor confirmation | Nothing |
| Can be advanced today | No — waiting on vendors | **Yes** |
| Cost of delay | Time | **Permanent. Unrecoverable.** |

v3 §17.5 option **(b)** is: store prices daily going forward and build genuine
point-in-time price history from now. The document is explicit —

> **(b) costs nothing but time and starts paying immediately — but only if it
> starts now**, which makes this the one open question with a deadline attached.

**Option (b) does not require a vendor decision.** It requires capture to start.
Every day without it is a day of point-in-time price history that cannot be
purchased later at any price, from any vendor, because no vendor sells the
unadjusted series as it stood on a past date. This is the same shape as the
survivorship-bias door ruling 5 closed, arriving on the price side — which is
precisely what §5.1 and the source map §7.1 both warn about, independently.

**The register already contains the reasoning.** `gqs-source-map.md` §7.1 says a
back-adjusted price times shares outstanding *"gives a market cap nobody ever
observed"* and *"it will pass every test that does not check for it
specifically."* **What the register does not contain is the deadline**, because
the question carrying it was dropped in the renumber.

---

## 5. Three consequences for work already scheduled

### 5.1 The R&D session is narrower than the closeout framed it

v3 **§13** already carries the full adjustment: the straight-line asset and
amortization equations, and the statement that adjusted values flow into **P1,
P2, R1, R2 and nowhere else.** Then:

> **Both adjusted and unadjusted scores must be computable in the same run**, so
> the adjustment's effect is measurable rather than asserted.

The Planner closeout offered "compute both and report the rank correlation" as
**option 2 of three** for settling §17.1. **The specification already mandates
it as a build requirement under every option.** So §17.1 is not *which
treatment* — both are computed regardless. It is **what is `L`**, and secondarily
whether the unadjusted series or the adjusted one is the one published.

That is a materially cheaper question than the one on the board, and it is
already half-answered: §17.1 names the candidates as `L` = 3 (software
convention), 5 (general), or sector-varying.

### 5.2 §13 confirms the data-coverage problem, and names the flag

v3 §13: *"Requires `L` years of R&D history; less ⇒ partial asset, flagged."*

The store holds **one quarter** — `coverage_window` reports `2026q2..2026q2`.
Prior-period comparatives inside each filing give some history, but not five to
eight years of it, and **the truncation is not uniform across companies.** It is
deepest for the long-programme research-intensive names, which are the entire
population §17.1 is about. A rank correlation computed against today's store
would return a number, look like an answer, and nothing would dispute it.

**This does not block the session — it sequences it.** The 45-quarter load is
built, unattended, ~34 h, restart free and confirmed (F-034). It is calendar
time, not work time.

**Unresolved and worth one query before anyone relies on my reading:** distinct
fiscal years of `us-gaap:ResearchAndDevelopmentExpense` per filer in the current
store. **My stated expectation is a mode of 2–3 years.** If it comes back at 5+,
I am wrong and the measurement can run today. Stating the expectation first is
what makes it a check rather than a number.

### 5.3 F-C is already fixed in v3, and F-D reveals a port item nobody has logged

**F-C does not hold against v3.** The register records it as a live defect:

> §2 goal 1 says the score is *"computed per ticker from SEC filings only"* and
> §5.1 names EDGAR as the sole source.

v3 §2 goal 1 makes no filings-only claim, and **v3 §5.1 is titled *"The
correction: two sources, not one"*** and states Source B as required with no way
around it. The v1→v2 change log, entry 2, records the fix and the reason it was
caught. **The Planner closeout's Part 5.2 lists this among the things the port
must rewrite. That work is already done** — in the document, by its author, a
year's worth of revision before we saw it.

**F-D holds, and opens something larger.** v3 §9.3 does route on market value of
equity in the manufacturing path. But **ruling 11 chose `Z'`, the private-firm
revision with book equity in X4 — and `Z'` is not one of v3's two variants.** v3
offers `Z` (manufacturing, market equity) and `Z″` (non-manufacturing, book
equity, different coefficients). `Z'` has its own coefficient set and is neither.

So ruling 11 does not select from §9.3; it **replaces** §9.3's routing. The
second-order effect is worth recording, because it moves a triage class:

> v3 §9.3: *"Formula routing depends on §17.2, which makes §17.2 load-bearing in
> two separate places."*

If `Z'` applies universally, **§9.3's routing disappears and §17.2 is
load-bearing in one place only** — §7.3's sector-relative ranking. §17.0 rates
§17.2 "Mixed" partly on that doubling. **Ruling 11 has already lowered §17.2's
weight and nothing records it.**

---

## 6. Proposed register changes

**The Planner proposes; the Builder applies.** Short names only — no numerals,
per the error record.

### Findings

| Name | Claim |
|---|---|
| `F-next/the-tdd-we-gate-is-not-the-tdd-we-hold` | The register's GQS section numbering is a different edition's. Crosswalk in §2 of this report. Artifact: machine-extracted heading list of `TDD-growth-score-v3.md` vs the register's references |
| `F-next/ruling-7-corrected-a-correct-reference` | D-010's original *"five open questions in its §17"* matches v3's header verbatim in scope. Ruling 7 reworded it to a section that in v3 is `insufficient_data` |
| `F-next/the-gate-is-short-a-result-changing-question` | §17.5 has no counterpart in the register. §17.0 rates it result-changing with a deadline. It is not OPEN-9 |
| `F-next/f-c-was-repaired-by-its-own-author` | The filings-only contradiction does not exist in v3. Port scope shrinks accordingly |
| `F-next/ruling-11-halves-17-2s-load-bearing` | `Z'` is not one of v3 §9.3's variants; adopting it removes the Z-routing dependency on §17.2 |
| `F-next/lineage-still-points-at-the-old-numbering` | `growth-model-lineage.md` §8 cites TDD §5.4 for R&D; v3 has it at §13. Lineage needs the same renumber the TDD got |

### Decisions for the owner

| Name | Proposal |
|---|---|
| `D-next/d010-condition-restated-against-v3` | **Reverse ruling 7.** Restate D-010's condition as *the five open questions in §17*. Record ruling 7 as struck with its reason visible, not deleted |
| `D-next/gate-table-renumbered-to-v3` | Rewrite `testplan.md`'s gate table against §19's five conditions, with §17.1 **and** §17.5 open |
| `D-next/price-capture-starts-now` | Adopt §17.5 option (b) provisionally and **start daily capture ahead of vendor selection.** Discardable if (a) or (c) is later chosen; unrecoverable if deferred |
| `D-next/z-prime-supersedes-9-3-routing` | Record that ruling 11 replaces §9.3 rather than selecting within it, and that §17.2's triage class moves |

**Delete nothing.** Ruling 7 keeps its text and its reason. The register's value
is that struck claims stay visible with why.

---

## 7. What I could not establish, and what I want from Code

1. **Which file was on disk 2026-09-23.** If a pre-v3 file was present and
   labelled v3, **all four of F-A through F-D were read against it**, and the
   `gqs-source-map.md` §-references need re-reading against v3 rather than
   renumbering. I can do that; the crosswalk is most of the work already.
   **This is the one thing that decides whether §5.3 above is the end of the
   re-read or the start of it.**
2. **Whether `TDD-growth-score-v3.md` should be committed into this repo.** It is
   currently an artifact that exists only in the owner's hands and in two agent
   contexts. **The register gates on a document it does not contain.** That is the
   same shape as the manifest that did not list itself.
3. **The R&D history query in §5.2** — owner-at-the-keyboard, one statement,
   read-only, expectation stated in advance.

**Nothing in this report contradicts anything in Code's closeout.** The two
closeouts are accurate about the repository; the mismatch is between the register
and a document that was never in it.

---

## 8. The honest column

I have read the two new documents once each, sections named in §1, today. **I
have not read v3 in full** — §7, §8, §9.1, §9.2, §10, §14, §15, §16 and Appendix
A are unread, and Appendix A is where the tag chains live, which is where the
port's real work sits.

I am also aware that this report is the second consecutive sitting in which a
fresh Planner has arrived, read the GQS documents, and produced a list of
defects in the register. **The first one was wrong about the most important
item.** Everything above should be reconciled against Code's own read of v3
before any of it is applied — which is what this report is for.
