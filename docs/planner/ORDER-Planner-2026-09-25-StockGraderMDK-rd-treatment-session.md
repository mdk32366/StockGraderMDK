# ORDER — the R&D treatment session — StockGraderMDK

**From:** Planner · **Date:** 2026-09-25 · **Session date: 2026-09-25 — today.**
**Scheduled by the owner 2026-09-25.** This is the session that **P-13** says was
deferred to "its own session" on day one and never scheduled. The deferral now
has a date, which is the whole of what P-13 asked for.

**Decides:** §11.1 / §5.4 — the treatment of research and development spending.
**Blocks until decided:** every scoring build order. See §5 below.

**Standing rules unchanged:** no credential reaches the Builder; anything against
the live cluster is owner-at-the-keyboard, one command at a time; report don't
fix; the repo is public (D-020).

---

## 1. The question

**Is R&D left as accounting rules treat it — an expense in the year incurred —
or capitalised as an asset and written down over an assumed useful life?**

It is genuinely open, and both sides cost something real:

- **Leaving it as an expense systematically penalises exactly the businesses a
  growth-quality model should rank highest.** Heavy R&D depresses earnings,
  returns on capital and reinvestment ratios, which are inputs to two of the five
  scoring blocks.
- **Capitalising inserts an assumption nobody discloses.** No filing states the
  useful life of research. Choosing three, five or eight years **is** the ranking
  for research-intensive companies — the choice is not a detail inside the model,
  it is the model, for that population.

---

## 2. Step 0 — the prerequisite check. Run this before choosing a path.

**The Planner's recommendation (§3, option 2) rests on a claim nobody has
verified: that the store holds R&D expense.** The closeout asserts it. It has not
been checked against the cluster.

**This is P-12's shape** — *a ruling that depends on a figure waits for the
figure* — and P-12 is in the error record because a window was ruled before
anyone measured bytes per row.

**One query, owner at the keyboard.** No credential in any line that gets pasted
back; `PGPASSWORD` via `Read-Host -AsSecureString`, DSN in keyword form:

```sql
SELECT count(*)                         AS rows,
       count(DISTINCT filing_id)        AS filings,
       min(period_end), max(period_end)
FROM   fact
WHERE  concept = 'ResearchAndDevelopmentExpense';
```

**Read the result as follows:**

| Result | What it means | Path |
|---|---|---|
| A substantial population across many filings | Option 2 is available | **Take option 2** |
| Present but thin, or one quarter only | Option 2 measures noise | **Option 1 now, option 2 when the 45-quarter load lands** |
| Absent | The concept is not loaded | **Option 1 now.** Do not rule on capitalisation blind |

**The store currently holds 2026q2 and 2015q2 only** — two quarters eleven years
apart, 3,368,813 facts. **A rank correlation computed on two quarters is not the
same evidence as one computed on the ruled 45-quarter window**, and the session
should say which it has.

---

## 3. The three ways to settle it, in the Planner's preference order

**1. Rule that version one does not claim to handle research-intensive companies
well, and state that limitation in the output.**
Cheapest, honest, reversible. **It unblocks the §13 gate today.** The cost is a
named weakness in the product's first version — which is a disclosure, not a
defect, provided it is actually disclosed.

**2. Compute both treatments and report the rank correlation.**
R&D expense is a filed figure. Scoring under both treatments and measuring how
far the ranking actually moves **converts an argument into a number**, and it is
what this project does with everything else. **The Planner recommends starting
here** — it is the one thing that became possible while the question sat, because
the facts now exist.
**Its cost is not small and the session should say so out loud:** it needs enough
of the scoring layer built to run twice, and the scoring layer is the thing the
gate is blocking. **If step 0 or the session finds that circularity binding,
option 2 is not available today** and the honest move is option 1 now with
option 2 as the revisit.

**3. Capitalise with a stated life and a sensitivity note.**
Defensible, and the most work. It inserts the undisclosed assumption deliberately
and measures what it does. **Not recommended as a first move** — it is option 2's
conclusion arrived at without option 2's evidence.

---

## 4. What the session must produce

**A ruling, recorded, with its reason and its reversibility stated.** Not a
direction of travel.

1. **A D-entry** naming the treatment chosen, what was rejected, and **the
   condition under which it would be revisited.** A ruling with no revisit
   condition is how §11.1 became P-13 in the first place.
2. **The §13 gate rows updated** — `docs/testplan.md`, the two rows reading
   **OPEN**. They are the same question and must move together.
3. **If option 1:** the limitation text itself, drafted, not deferred. *"State
   that limitation in the output"* is the ruling; an undrafted disclosure is the
   deferral wearing a different hat.
4. **If option 2:** the decision that the correlation changes, named **before**
   the number is computed — `F-next/a-measurement-that-decides-nothing` (F-035)
   applies to this session as much as to any other. *What rank correlation would
   make us capitalise?* Answer it first, or the number arrives and nothing
   disputes it.

---

## 5. What this unblocks, precisely

`docs/testplan.md`, **GQS §13 completeness gate**:

| §13 condition | State before this session |
|---|---|
| Any §11 question unratified | **OPEN** — 11.1 deferred (ruling 12); 11.2, 11.3, 11.4 ruled |
| §5.4 R&D treatment unresolved | **OPEN** — the same question as 11.1 |

**§11.1 is the only open §11 question.** Downstream, from
`docs/gqs-source-map.md`: the **reinvestment rate** (capex, R&D and acquisitions
over NOPAT) is **gated by §11.1 — the R&D treatment decides it**, and through it
two of the five scoring blocks.

**Two §13 conditions remain unconfirmed pending v4** — the eligibility table and
placeholder metrics. **Ruling §11.1 does not by itself open the gate**, and the
session should not claim it does. It removes the one condition that has been
open since day one and cannot be closed by anybody else.

**Ingest is unaffected and proceeds either way.**

---

## 6. The session that follows, and why it is not this one

**§5.2 — port the scoring specification to this codebase.** The spec was written
2026-09-09 for a different project; the owner ruled it be revised rather than
patched. It names a migration tool this project rejected, an agent that does not
exist here, and a trading function with no equivalent; its claim that the score
comes **from SEC filings only** is false as written, since a quarter of the score
needs market prices.

**It is a separate session and must stay separate.** Folding the port into this
one is how a decision session becomes a build session and the decision does not
get made — which is the shape that produced P-13.

---

## 7. The rule this order exists to satisfy

> **A deferral without a date is a deferral without an end.** — P-13

The date is **2026-09-25**. If the session does not happen today, **the next
Planner does not re-defer it — it gets another date, written down, in this
file.** An order that slips silently is the same failure with a document attached.
