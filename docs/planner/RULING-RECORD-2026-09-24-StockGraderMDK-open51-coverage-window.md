# RULING RECORD — Owner → Planner → Code — StockGraderMDK: OPEN-51, coverage window

**From:** Planner, recording an owner ruling received 2026-09-24
**Issued:** 2026-09-24, first issue
**Answers:** §5 of `HANDOVER-Planner-2026-09-24-...-fact-slice.md`

---

## 1. The ruling

**The fact slice loads the 45 most recent FSDS quarters** — roughly 2015q1
through 2026q2, trimming the oldest end of the archive's usable range.

**Measurement comes first regardless.** One quarter into a local cluster, table
and index sizes taken, multiplied by 45. **Report the number before loading 45.**

Loading 45 quarters to find out where we sit is measuring by doing the expensive
thing. The difference matters at the failure end: if it does not fit, a
measurement costs an hour and a load costs deleting from a database that already
holds the data. **45 is then a decision rather than an experiment.**

---

## 2. Why the oldest quarters are the right ones to drop

Recorded because *recent data is more useful* is the weaker argument and would
not survive scrutiny later.

**The archive cannot supply 2008 under any option.** It begins 2009q1, is not
usable until about 2011q4 (OPEN-42), so every available window is entirely
post-crisis. **No choice here buys the event a durability model would most want
to have seen**, and that is a property of the source rather than of this ruling.

**The fifteen quarters dropped — roughly 2011q4 to 2014q4 — are the benign
recovery years.** They are the weakest available test of whether a growth-quality
score identifies companies that survive stress. The 2015–16 industrial and energy
recession and the 2020 drawdown both sit **inside** the 45.

**So the marginal validation value of the dropped quarters is lower than their
row count suggests**, which is the actual argument. Storage is the occasion, not
the reason.

---

## 3. The condition — coverage is recorded as data

**Which quarters are loaded must be answerable from the store, not from anyone's
memory or from a handover.**

Without it, someone runs a 2013 backtest against a store beginning in 2015 and
gets a **well-formed, nearly empty answer that looks like a result** — the code
correct, the query valid, the coverage the thing nobody stated. That is OPEN-42's
nominal-versus-usable problem arriving from our own choice rather than from the
SEC's phase-in, and it is the ninth instrument on the list.

**Two requirements:**

1. **Loaded quarters are recorded as rows**, with their per-quarter fact counts,
   so the store can answer *what does this cover?* directly.
2. **Any validation states its window in its own output**, not in a document
   beside it. A validation result that does not carry its coverage is not
   interpretable, and the one that silently has none is worse than an error.

**This does not change §4.3's rule.** *Store, don't filter* still governs
everything inside the loaded window — `prevrpt`, dimensions, superseded facts.
The coverage boundary is a **load decision recorded as data**, not a filter
applied to data we hold. The distinction is what keeps it honest: we are not
hiding quarters we have, we are recording which ones we took.

---

## 4. If the measurement says 45 does not fit

Report and stop. The §5 order of preference stands unchanged:

1. Narrow the **concept** set to the TDD's §4 blocks plus a margin.
2. Increase the disk.
3. **Not** narrowing dimensions.

**The reversibility argument is what makes concept-narrowing acceptable and
dimension-narrowing not.** FSDS quarterly archives are immutable once published
and re-readable indefinitely, so a narrow concept set can be widened later from
an archive that has not changed. The 60.7% of dimensioned rows is the entire
basis of OPEN-36; discarding it would leave a store indistinguishable from the
companyfacts one we rejected, and the ruling would have bought nothing.

**The same reversibility applies to the window itself.** Quarters not loaded
today can be loaded later from the same unchanged archives. That is worth stating
so the 45 is understood as a starting position rather than a permanent bound.

---

## 5. Unchanged

OPEN-48, 49, 50 still come before the build — `version` and filer extension
tags, `segments` truncation, `adsh` formatting. None is inferable from samples.

OPEN-44's per-source answer — FSDS archives should be immutable and
`submissions.zip` should not — is a cheap fetch-twice test and belongs with them.

Run phase gated as before: OPEN-25, OPEN-27, OPEN-30, OPEN-21, OPEN-33, plus
slice 1's own run.
