# HANDOVER — Planner → Code — StockGraderMDK: migration 0001, design and review

**From:** Planner · **Issued:** 2026-09-23, first issue
**Runs:** now. Does not wait on the drill.
**Governed by:** D-021 (forward-only numbered SQL migrations with verification
queries, no Alembic), ruling 5, TDD §5.1.

---

## 0. What this block is, and is not

**Design and review, not deployment.** Produce the migration and its verification
queries, test the DDL against `stockgrader_scratch`, and report. **It is not run
against `stockgrader` in this block** — the live database is about to be a
different cluster, and a migration applied to the one being retired is work
thrown away.

Testing against scratch is a cluster mutation. Report it per D-034.

**Nothing in this block touches scoring.** §13 refuses the TDD for build and that
stands. What follows is the fact store, which §10 puts first and which is the
same work whichever way §11.1 lands.

---

## 1. The three properties this migration has to carry

These are unaffordable to retrofit. Everything else in the schema can be added
later; these cannot.

**1.1 — Identity is CIK, not ticker.** Ruling 5, and EODHD's own documentation
warns the same thing from the vendor side: a ticker may now belong to a different
company, and symbols get reassigned. A universe keyed on ticker is wrong in both
directions — it loses dead companies and silently merges live ones.

Ticker is a **time-bounded attribute of a filer**, not an identity. It needs
validity bounds so that a historical query resolves the ticker that was in force
then, not the one in force now.

**1.2 — Every fact carries its filing date and accession number.** TDD §5.1. The
score for any historical date is computed only from facts filed on or before that
date. This is the property that makes future validation possible and it is the
one the TDD says is expensive to retrofit and cheap to build in now.

**1.3 — The universe is derivable from filing history.** Ruling 5. If the schema
can answer *which CIKs had filed a 10-K in the three years before date D*, the
point-in-time universe falls out of the same tables as the point-in-time facts,
and survivorship is handled structurally rather than by a list someone maintains.

---

## 2. The constraint that matters most, stated as a prohibition

**An amended filing creates new facts. It never updates existing ones.**

TDD §13 names this specifically: an overwrite-on-amendment implementation
silently destroys the point-in-time property and **must be caught in review, not
in backtest.**

**Design it so the wrong thing is hard, not merely discouraged.** The natural
temptation is a unique constraint on something like (cik, concept, period),
because that looks like the right key for a financial fact. That constraint is
exactly what forces an upsert when a 10-K/A arrives, and the upsert is the defect.
The uniqueness that is actually true includes the accession.

**Report your key choice and say what it makes impossible.** That sentence is
what review checks, and it is the review the TDD asks for.

---

## 3. Scope for 0001

**In:**
- Filers, keyed on CIK, with SIC from EDGAR submissions metadata — SIC still
  does the §5.3 eligibility exclusions for financials and REITs, even though
  ruling 13 replaced it as the valuation ranking basis.
- Filer-to-ticker with validity bounds.
- Filings: accession, CIK, form type, filing date, period of report.
- Facts: concept, value, unit, period, and the filing they came from.

**Out of 0001, deliberately:**
- **Prices.** The vendor is unchosen (OPEN-9) and two disqualifying properties
  are unanswered. A price schema written before the vendor is known will be
  written to the wrong shape. When it does land, as-traded closes and adjustment
  factors are stored **separately** — a back-adjusted close times shares
  outstanding is a market cap nobody observed.
- **Archetypes.** The classifier is unspecified.
- **Anything scoring-shaped.** Blocked.

**Open to your judgment:** whether facts are one table or split by statement, and
how units and contexts are modelled. State the reasoning; I am not ruling on
shape I have not thought about as hard as you are about to.

---

## 4. Verification queries — D-021's requirement

Per D-021 each migration carries them. The ones worth having here are the ones
that would fail if a property in §1 were absent:

- A point-in-time query: facts as of a past date, returning nothing filed after it.
- An amendment query: a concept with an original and an amended value, showing
  **both rows**, distinguishable by filing date.
- A universe query: CIKs with a 10-K filed in a window, keyed on CIK alone.
- A ticker-reassignment query: the same ticker resolving to different CIKs in
  different periods, if you can construct the case.

The fourth may not be constructible with synthetic data. If not, say so rather
than writing one that passes trivially.

---

## 5. Report

The migration, its verification queries, the key choice and what it forecloses,
the scratch test results, and anything in §3 you judged differently and why.

**Do not run it against `stockgrader`.** After the cutover it runs against
`stockgrader-db-r1`, and that is a separate block.
