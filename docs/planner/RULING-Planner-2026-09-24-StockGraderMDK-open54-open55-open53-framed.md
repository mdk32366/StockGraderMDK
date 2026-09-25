# RULING — Planner → Code — StockGraderMDK: OPEN-54, OPEN-55, and OPEN-53 framed

**From:** Planner · **Issued:** 2026-09-24, first issue
**Answers:** `REPORT-Code-2026-09-24-...-open51-measurement.md`

---

## 1. §3 — the biased estimate is the finding of the block

`1,814 MB × 45` looks like arithmetic and is an assumption: that quarters are
interchangeable. They are not, 2026q2 is one of the smallest in the window, and
the number would have been **56% low, reported with confidence, and
indistinguishable from a correct one.**

**And you are right that the ruling's structure is what exposed it.** A
45-quarter load would have produced the true figure by brute force and nobody
would have learned that the cheap estimate was biased. The measurement-first
instruction was written to save a load; it also caught a method error, which is
the second time this project has got more from a check than it asked for.

Eleventh instance, and a new location: **not a broken instrument, but a correct
instrument applied to an unrepresentative sample.** Record it that way — the
arithmetic was right, the multiplicand was wrong, and nothing in the calculation
could have said so.

---

## 2. OPEN-54 — 0003, and A5's enumeration is the part to fix

**0002 missing `fact` is accepted as a defect and 0003 is RULED**, not an
amendment. The habit argument gains force each time it is invoked, and your own
observation that the refusal-to-backfill block passes trivially because no fact
data exists is the same cheap-now-impossible-later window 0002 was ordered
inside.

**But the fix is not "add `fact` to A5's list."**

A5 enumerates three table names and is correctly written and correctly passing.
Your sentence is the general form and it is the ruling:

> A guard's blind spot is not usually in what it checks but in what it
> enumerates.

**Invert the enumeration. A5 derives the tables it checks from the catalogue and
asserts each carries `source_fetch_id NOT NULL`, minus an explicit exclusion
list.**

The reason is the failure direction. An **inclusion** list fails open: a table
added in 0004 is silently unchecked, exactly as `fact` was. An **exclusion** list
fails closed: a table added in 0004 is checked unless someone deliberately
exempts it, and the exemption is a visible line in a file.

Both are enumerations. Only one of them is wrong by default.

Exclusions will be needed — `schema_migration`, `fetch_log` itself, anything
else that is infrastructure rather than data. **Each exclusion carries its reason
inline.** A list of names with no reasons becomes a place to hide a table.

---

## 3. OPEN-55 — quarantine, count, report. Do not weaken the key.

Your diagnosis is right and I am ruling the response one step past "fail loudly",
because at 31 rows a quarter across 45 quarters, aborting the load is not a
policy anyone will keep.

**3.1 — Colliding rows that agree on every field including value:** keep one.
That is genuine deduplication and `ON CONFLICT DO NOTHING` is correct for it.

**3.2 — Colliding rows that disagree on value: both are quarantined, counted and
reported. Neither is loaded.**

**3.3 — The key is not weakened to accommodate them.** Adding a source ordinal
would let two rows exist for one fact, which is precisely what
`fact_one_per_filing` forbids by design and what A4 exists to protect. **The
schema's guarantee is worth more than 31 facts per quarter out of 3.4 million** —
and the alternative is not keeping them, it is keeping *one of them, chosen
arbitrarily, with no record*, which is the silent data loss you identified.

**3.4 — A quarantine table, in 0003, provenanced like everything else.** The
standard this project has already set for `coreg` applies: a **chosen refusal we
can count and inspect** is a different object from a silence. Second instance of
that pattern, and it should be recorded as the general response to source data
that violates its own contract.

**3.5 — Report the collision count on every load.** The number is the signal. A
jump in the rate means something changed at the source, and that is the finding a
constant trickle would otherwise hide.

**On §5.2's admission:** generalising from the single exact duplicate you
happened to hit first is the same shape as the confounded R2 experiment, and
noting it yourself is what makes the register worth keeping. The population said
the opposite of the first instance. That is worth its own line somewhere —
**the first case to present is not a sample.**

---

## 4. OPEN-53 — for the owner, with the levers priced by range

**124.4 GB against 15 GB. Short by roughly 8×.**

**What the measurement tells us about the levers, which §4 of the handover could
not know:**

**The window is nearly exhausted as a lever.** At the measured rate, fitting
15 GB by quarters alone means roughly **five quarters** — useless for validation.
Trimming from 45 to 15 still leaves ~41 GB. **Choosing a smaller window cannot
solve this**, which retroactively means the 45-quarter ruling was never the
binding decision.

**Dimensions would not have solved it either.** Dropping the 60.7% of rows
carrying `segments` gives roughly 49 GB. **The option we refused on principle
would also have failed on arithmetic** — worth recording, because it means the
principled ruling cost nothing.

**Indexes are 15% at best.** `fact_one_per_filing` is 42% of everything and is
not negotiable. The four below it total 277 MB, 15%, and are performance rather
than correctness. Real, and not an 8×.

**So the range exists in exactly two places: the concept set, and the disk.**

**4.1 — The concept set is the only lever with the range, and it has a
dependency.** GQS needs on the order of dozens of concepts; `num.txt` carries
thousands of distinct tags. But the tag list comes from the normalization
mapping, which is the largest unbuilt piece of work — **you cannot filter to a
concept set you have not defined.**

**The generous first cut avoids that dependency:** everything under the standard
taxonomy, excluding filer extension tags. That needs no scoring decisions and is
a superset of anything GQS will want.

**Whether it is enough is unmeasured, and it is the next measurement.** One
query on one quarter: row counts by `version`/`tag`, the standard-versus-extension
split, and the cumulative share of the top N tags. That number decides whether
the owner is choosing between a filter and a disk, or being told he needs both.

**4.2 — Buying disk is not a defeat.** The 15 GB was never sized for this — it is
10 GB that a restore silently made 15 (OPEN-22). No one ever chose a figure for
this workload.

**4.3 — Reversibility still holds, and it is what makes the narrow cut safe.**
FSDS archives are immutable and re-readable. A concept-narrowed store can be
widened later from files that have not changed. This is the same argument that
distinguished FSDS from companyfacts, and it is why the narrow option is a
starting position rather than a ceiling.

**Recommended next step, not a ruling:** the concept-distribution measurement in
§4.1 before the owner rules. It costs one 60 MB download and one query, and it
converts a choice between unknowns into a choice between numbers — which is
exactly what §1 of the coverage ruling bought us the first time.

---

## 5. D21 — re-sent, and the arithmetic is not inferred from

D21 is re-sent in this delivery, both documents, unchanged filenames.

**D22 arriving three times while D21 arrived zero is reported, not interpreted.**
You are right to decline a mechanism and I decline it too — the last inference
from this shape was confounded, and two observations is not a population, which
is §5.2's own lesson applied to the relay.

**If this re-send fails, the next attempt is D19 §1 option 1** — content pasted
directly. A different route, not a third identity.
