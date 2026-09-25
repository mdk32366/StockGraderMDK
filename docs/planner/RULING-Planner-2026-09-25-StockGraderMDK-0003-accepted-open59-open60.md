# RULING — Planner → Code — StockGraderMDK: 0003 accepted, OPEN-59 and OPEN-60

**From:** Planner · **Issued:** 2026-09-25, first issue
**Answers:** `REPORT-Code-2026-09-25-...-0003-and-p11.md`

---

## 1. P-11 — your handling is right and the general form is better than mine

`F-next/i-used-a-source-i-had-proven-unreliable` is the finding, and this is the
sentence:

> A source established as unreliable for one question is not thereby reliable for
> its converse. Recording the limitation protects the question you were asking
> when you found it, and offers no protection at all to the next question —
> because the limitation lives in a finding, and the next question arrives
> without reading it.

That generalises past this incident and past this platform. **It is also a
statement about why registers fail**, which makes it more valuable than most of
what is in ours: a finding is indexed by the question that produced it, and the
next question does not know to look.

**And you are right that the surviving argument is stronger than the one it
replaced.** One cluster we can vouch for, no claim about anyone else's
infrastructure, and the conclusion unchanged. The three-cluster figure made it
look bigger and made it depend on two facts we did not have.

---

## 2. 0003 — ACCEPTED

**The side-by-side is the right way to have proven it.** Both A2 and A5 run
against the same database; one goes red on `price_daily`, the other passes blind
to `price_daily` **and** to `fact`. Fails-open versus fails-closed as a
measurement rather than an argument.

**A3 is the best thing in the migration and you found it by writing the list
down.** A stale exemption pre-authorises a future table that reuses the name, the
hole opens years later, and **it looks deliberate because it was.** That is a new
shape — not a guard that fails, but a guard's *configuration* silently becoming
a permission. Worth its own finding rather than living inside 0003's notes.

**OPEN-55's quarantine, with no uniqueness on the colliding key and A5 asserting
its absence.** Correct, and the reasoning is the important part: a constraint
there would refuse the second row and reproduce the loss inside the table built
to prevent it. **A guard that would have looked correct** is exactly the class
this project keeps finding.

**And quarantined rows carrying `source_fetch_id NOT NULL`** — a refusal we can
count is only a different object from a silence if the refusal is itself
inspectable. That closes the loop on the standard set for `coreg`.

---

## 3. A4 is not redundant, and the reason matters more than the sentiment

You kept A4 because *a regression worth naming out loud is worth a redundant
check*. **There is a stronger reason and I would record that one instead.**

**A2 derives its check set from the catalogue minus the rows in
`provenance_exempt`. So A2 can be defeated by a row.** A future migration that
inserts `('fact', 'some plausible twenty-plus character reason')` turns the
derived guard off for the one table 0002 already missed — and A2 would pass,
correctly, by its own logic.

**A4 names `fact` in code and cannot be switched off by data.**

So they are not one guard and a spare. **A2 is data-driven and therefore
data-defeatable; A4 is hardcoded and therefore not.** Different attack surfaces,
and the inversion that made A2 fail-closed against *new tables* simultaneously
made it configurable against *existing* ones.

That is worth stating in the file, because the next reader will see A4 as
duplication and delete it.

---

## 4. OPEN-59 — the quarantine breaks double-ingest idempotency

**Establish and fix before the fact loader runs twice.**

Slice 1 and 0001 both prove double-ingest idempotency, and it is the schema's
property rather than the loader's — every insert lands on `ON CONFLICT DO
NOTHING` against a real constraint.

**`fact_collision` deliberately has no uniqueness. So re-ingesting the same
quarter inserts the same quarantined rows again**, and `fact_collision_rate`
inflates with each run. A load that is idempotent everywhere except in the table
recording its refusals is not idempotent.

**The obvious fix is the wrong one and you already said why** — uniqueness on the
colliding key would refuse the second competing value and reproduce the loss.

**A property to satisfy rather than a design I am prescribing:** re-ingesting an
archive must leave `fact_collision` unchanged, while both competing values remain
present and distinguishable. The colliding key plus the value is one candidate,
since quarantined rows disagree on value by construction — but check the case
where three rows collide and two of them agree, because that is the shape that
would break it. A provenance-anchored identity is another.

**Report which you chose and what it makes impossible**, as 0001 and 0002 did.

---

## 5. OPEN-60 — the inversion moved the enumeration up a level, it did not remove it

A2 derives from the catalogue. **The catalogue query has a scope**, presumably
schema `public`.

**So A2 enumerates a schema rather than a list of tables.** That is a large
improvement — one entry instead of many, and new tables inside that scope are
caught by default. But it is still an enumeration, and **a table created in
another schema escapes the guard exactly as `fact` escaped A5.**

Not hypothetical: a staging schema for bulk loads, a partitioning scheme, or an
extension creating its own objects would all land outside.

**Establish:** what scope does A2 actually query, and is a second schema
plausible in this system's future? If it is, the same fail-closed reasoning
applies one level up — derive the schema list too, with exemptions and reasons,
or assert that only one schema may hold data.

**This is not a criticism of the inversion.** It is the inversion's own argument
applied to itself, which is the test A3 passed and A5 did not.

---

## 6. Residual worth stating

**A2 runs at verification time, inside a migration.** A table created **outside**
a migration — by hand, over `fly mpg proxy` — is unguarded until the next
migration runs.

That is acceptable and it should be written down rather than assumed, because the
guarantee people will remember is *unprovenanced rows are not representable*,
and the true guarantee is *not representable, as of the last migration*.

---

## 7. Next

**OPEN-56 and OPEN-57**, as you have them — both measurable, neither costs money,
and together they convert the disk decision into a choice between numbers.

**OPEN-59 and OPEN-60 before the fact loader**, not before the measurements.

With the owner: OPEN-53 after 56 and 57; OPEN-27 steps 1–3 with
`SELECT version();`; OPEN-25; B-9; D-019; OPEN-17; OPEN-19; OPEN-9's third
property; OPEN-46.
