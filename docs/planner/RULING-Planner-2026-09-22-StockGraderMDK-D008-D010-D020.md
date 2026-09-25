# RULING — Planner → Code — StockGraderMDK: D-008, D-010, D-020 ruled; fund scoring

**From:** Planner · **Date:** 2026-09-22
**Owner rulings received.** Record all of this in PR-5; none of it starts code.
**Blocking still:** the Planner has not read GQS v3 or `growth-model-lineage.md`.

---

## 1. D-008 — RULED

US-listed common stocks, US mutual funds, **and US ETFs**. ETFs file N-PORT, so
fund-versus-ETF overlap comes almost free, and it is the comparison most people
actually want.

## 2. D-010 — RULED, with a condition that is not yet met

**The stock score is GQS v3.** Its four blocks, its integrity gate, its
`insufficient_data` fourth state, its point-in-time requirement, and its
attribution of score moves (fundamentals deteriorating versus price rising) are
adopted as the stock-side design.

**Condition:** GQS v3's own header says it is a draft with five open questions in
its §17 requiring owner ratification before a build order. **Those five are
ratified, or the build order for scoring does not issue.** Adopting a draft
without answering the questions its author flagged is how a draft becomes
doctrine by accident.

**A-016 — the Planner has not read GQS v3.** Everything above is taken from the
Builder's summary. A summary is not knowing (Principle 8). The TDD and
`growth-model-lineage.md` go to the Planner before any scoring design work.

## 3. D-028 — asset-class scope for v1: equity only. RULED.

Bonds are out of scope for this version and get their own analysis later. That
ruling has a hard consequence that must be built, not just noted:

**A fund whose non-equity weight exceeds a stated floor returns
`insufficient_data`, never a stock-only score computed over the equity part.**
A balanced fund that is 40% bonds is not a fund we scored badly — it is a fund we
cannot score. Rendering those two the same way is the plausible-and-wrong shape
Principle 11 is about.

## 4. D-027 — fund scoring: look-through, plus fund mechanics. PROPOSED.

The owner's framing is right: a fund is an amalgam of the same securities, and
look-through weighted scoring is the natural design. **It is necessary and not
sufficient**, and the gap matters more than it looks.

**Part A — look-through quality.** Weight each holding's GQS by its portfolio
weight.

**Part B — fund mechanics, which no amount of look-through can see.** Expense
ratio, loads, turnover and its tax drag, manager tenure, and concentration. The
published research is unusually consistent here: **cost is the strongest single
predictor of long-run fund outcomes, stronger than anything about the holdings.**
The same basket of excellent businesses at 1.4% with 90% turnover and at 0.03%
buy-and-hold are not the same investment, and a pure look-through score cannot
tell them apart. A buy-and-hold suitability score that ignores cost would be
wrong in the most expensive possible direction.

**Four traps this design has to defuse, each with a required behaviour:**

1. **The renormalisation trap.** Dividing by resolved weight assumes the
   unscored holdings look like the scored ones. Never renormalise silently.
   Report the weighted mean **and** the share of fund weight it was computed
   over, always, in the same response.
2. **Coverage floor.** Below a stated fraction of scoreable weight, the answer is
   `insufficient_data` with its reason, not a number. Same floor mechanism as
   D-028's bond rule.
3. **Date mismatch.** Holdings are quarter-lagged; stock scores are current. A
   look-through score is *today's score of what they held last quarter*. The
   response carries **both** dates, and the label says which is which. It is
   never presented as a current portfolio.
4. **Reason codes, not blanks.** Every unscored holding carries why:
   `NON_EQUITY`, `NO_FUNDAMENTALS`, `UNRESOLVED_IDENTIFIER`, `FOREIGN_LISTING`,
   and so on.

**Pre-registration required before the fund score is computed on real data.**
The honest null is not "does the fund score do something." It is:

> **Does look-through quality add anything over expense ratio and turnover
> alone?**

Write down, before you look, what result would mean it does not — and report that
result if that is what you get. This is the PharmFoldMDK §4 lesson applied
before the fact instead of after.

## 5. D-020 — RULED. The observable, as the owner stated it.

Development is complete when **all four** are true:

1. Scores exist across the ruled universe (D-008), not a sample.
2. A portfolio can be constructed from those scores and tracked over time.
3. That tracking has run long enough to say whether the scoring system works.
4. The API is available to an external consumer — a bot building or tracking its
   own portfolio, watching a stock, fund, or ETF.

Then the repo goes private. Until then it stays public, with the accepted risk
recorded in D-020's amendment.

**Two things this trigger needs to become checkable, both owner rulings:**

- **How long is "a stretch of time"?** Name it now — a number of months — because
  named afterwards it becomes however long it took to get a result somebody
  liked.
- **What result would mean the scoring system does *not* work?** Write it before
  the portfolio starts, not when the numbers arrive. Criterion 3 is a validation
  study, and a validation whose success criteria are set after the data exists is
  a rationalisation. GQS v3 already pre-registers at the component level; this is
  the same discipline at the portfolio level.

Condition 4 is also, incidentally, "the first user who is not you" — the trigger I
thought would never fire. It fires.

## 6. New assumptions

- **A-014** — enough of a typical fund's weight resolves to securities that carry
  a GQS for a look-through score to mean anything. Falsified when scoreable
  weight for common funds sits below the floor. Consequence: the fund score is
  `insufficient_data` for the funds people most want scored, and Part B carries
  the whole thing.
- **A-015** — quarter-lagged holdings are close enough to current holdings that a
  look-through score is informative. Falsified by high-turnover funds, where last
  quarter's basket is not this quarter's. Consequence: the score describes a
  portfolio that no longer exists. Mitigation: report turnover alongside it.
- **A-016** — as above, the Planner has not read GQS v3.

## 7. PR-5 additions

On top of the already-ruled scope: D-008 RULED, D-010 RULED with its condition,
D-027 PROPOSED, D-028 RULED, D-020 rewritten with the four-part observable and
the two open sub-rulings, and A-014 to A-016.

## 8. [OWNER]

1. **Phase 0 steps 1–2** — the cluster and the recovery credential. Still the
   only thing blocking the Builder.
2. **GQS v3 and `growth-model-lineage.md` to the Planner**, plus ratification of
   the TDD's five §17 questions.
3. **The two D-020 sub-rulings** in §5: the tracking window, and what failure
   would look like.
4. Security housekeeping at close: the API key out of Downloads.
