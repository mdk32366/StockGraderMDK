# ORDER — the R&D treatment session — StockGraderMDK — r2

**From:** Planner (relayed and corrected by Code) · **Date:** 2026-09-25
**Session date: 2026-09-25 — today.** Unchanged.

**Supersedes** `ORDER-Planner-2026-09-25-StockGraderMDK-rd-treatment-session.md`,
issued earlier today and merged in `2c40e35`. **That issue is wrong in three
ways and is superseded rather than deleted**, per the rule that a revision gets a
marker and says what it supersedes.

**What changed, and why:**

1. **The store holds ONE quarter, not two.** The first issue said *"2026q2 and
   2015q2 — two quarters eleven years apart, 3,368,813 facts."* **The cluster's
   `coverage_window` reports `2026q2..2026q2`.** The two-quarter load was
   **F-034's restart drill against a local throwaway cluster**, and 3,368,813 is
   the **one-quarter** figure. Code conflated the drill with the cluster. This
   matters because the whole of §2 below turns on how much history exists.
2. **The numbering is v3's.** The question is **§17.1**, not §11.1. The register
   has been gating on a different edition's section numbers — see
   `REPORT-Planner-2026-09-25-...-tdd-v3-numbering-and-ruling-7.md` and **F-037**.
3. **"Compute both" is not a settlement option.** v3 **§13** already mandates it
   as a build requirement. The first issue inherited it from the closeout as
   option 2 of three. It is not an option; it is the floor.

**Also new, and the reason to read §5:** the gate is short a second
result-changing question, and that one has a deadline. **F-038.**

---

## 1. The question, as v3 actually states it

`TDD-growth-score-v3.md` §17.1, verbatim:

> Adjust per §13, or score unadjusted GAAP? If adjusted, `L` = 3 (software
> convention), 5 (general), or sector-varying? **This materially reorders every
> research-intensive company.**

**So it is two questions, not one**, and the first issue collapsed them:

- **(a) Adjust at all?** §13 opens *"If §17.1 ratifies the adjustment"*, so this
  is still live. The first issue was wrong to imply it was settled.
- **(b) If adjusted, what is `L`?** Three named candidates. **This is the part
  that is cheaper than the closeout framed it**, because the candidates are
  enumerated in the document rather than open-ended.

v3 §13 carries the full adjustment already — the straight-line asset and
amortization equations, and the statement that adjusted values flow into **P1,
P2, R1, R2 and nowhere else.** **The session does not design the adjustment. It
ratifies it and picks `L`.**

---

## 2. Step 0 — the prerequisite, and it is now the binding constraint

v3 §13: *"Requires `L` years of R&D history; less ⇒ partial asset, flagged."*

**The store holds one quarter.** Prior-period comparatives inside each filing
give some history, but not three to eight years of it, and **the truncation is
not uniform across companies** — it is deepest for the long-programme
research-intensive names, which are the entire population §17.1 is about.

**One query, owner at the keyboard, read-only.** No credential in any line that
gets pasted back; `PGPASSWORD` via `Read-Host -AsSecureString`, DSN in keyword
form:

```sql
SELECT n_years, count(*) AS filers
FROM (
  SELECT filer_id, count(DISTINCT fiscal_year) AS n_years
  FROM   fact
  WHERE  concept = 'ResearchAndDevelopmentExpense'
  GROUP  BY filer_id
) t
GROUP BY n_years ORDER BY n_years;
```

**Stated expectation, before the number arrives: a mode of 2–3 years.** Stating
it first is what makes this a check rather than a number (F-035, F-A's rule).

| Result | Meaning | Path |
|---|---|---|
| Mode 2–3 years | As expected; too thin for `L`=5 | **Ratify (a); defer `L` to after the 45-quarter load** |
| Mode 5+ | The Planner's expectation is wrong | **`L` can be chosen on evidence today** |
| Concept absent or negligible | Not loaded | **Ratify (a) only. Do not pick `L` blind** |

**This sequences the session; it does not block it.** The 45-quarter load is
built, unattended, ~34 h, restart free and confirmed (F-034). **Calendar time,
not work time** — it can start today regardless of how §17.1 lands.

---

## 3. What the session must produce

1. **A D-entry ratifying or rejecting the §13 adjustment**, with its reason and
   **a stated revisit condition.** A ruling with no revisit condition is how this
   question became P-13.
2. **`L`, or an explicit deferral of `L` with the load as its end condition.**
   "Deferred until the 45-quarter load completes" is a date-bearing deferral.
   "Deferred to its own session" is P-13 again.
3. **The §19 gate rows updated** — and note they are **§19**, not §13. The
   register's gate table is numbered against v1 and needs the crosswalk applied.
   **Do not update the old table as though it were current.**
4. **Not a rank correlation, unless the decision it changes is named first.**
   Both scores are computable by §13 mandate; computing them proves nothing on a
   one-quarter store.

---

## 4. What this unblocks, corrected

`TDD-growth-score-v3.md` **§19** is the completeness gate. §17.1 is **one of
two** result-changing questions under §17.0's triage, not the only one.

Downstream, from `docs/gqs-source-map.md`: the **reinvestment rate** is gated by
this question, and through it two of the five scoring blocks.

**Ruling §17.1 does not open the gate.** §17.5 remains open, and two further §19
conditions are unconfirmed. **Ingest is unaffected and proceeds.**

---

## 5. The adjacent item, which may outrank this one

**§17.5 — price source and split adjustment. New in v2, so no v1 reader ever saw
it, which is why the register has no counterpart for it at all.** v3 §17.0 rates
it result-changing, and v3 §17.5 closes:

> **(b) costs nothing but time and starts paying immediately — but only if it
> starts now**, which makes this the one open question with a deadline attached.

**It is not OPEN-9.** OPEN-9 is *which vendor*, blocked on three vendor
confirmations. §17.5 option (b) — capture daily prices going forward — **needs no
vendor and is blocked by nothing.** Every day without it is point-in-time price
history that cannot be bought later at any price, because no vendor sells the
unadjusted series as it stood on a past date.

**The register already holds the reasoning and not the deadline.**
`gqs-source-map.md` §7.1: a back-adjusted price times shares outstanding *"gives
a market cap nobody ever observed"* and *"it will pass every test that does not
check for it specifically."*

**This is not this session's ruling and is deliberately not folded in** — that is
how a decision session becomes a build session and the decision does not get
made. **But if only one thing is ruled today, the case for it being §17.5 is
that §17.1 gets no worse by waiting and §17.5 does.**

---

## 6. The rule this order exists to satisfy

> **A deferral without a date is a deferral without an end.** — P-13

The date is **2026-09-25**. If the session does not happen today, **it gets
another date, written down, in this file.** An order that slips silently is the
same failure with a document attached.
