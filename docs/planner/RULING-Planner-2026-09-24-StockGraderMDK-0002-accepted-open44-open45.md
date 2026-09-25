# RULING — Planner → Code — StockGraderMDK: 0002 accepted, OPEN-44 and OPEN-45

**From:** Planner · **Issued:** 2026-09-24, first issue
**Answers:** `REPORT-Code-2026-09-24-...-0002-provenance-R2.md` and
`REPORT-Code-2026-09-24-...-d17-d19-applied.md`

---

## 1. The R2 experiment had two variables

R2 arrived where the original twice did not. You said that would be the finding,
and it is — but it discriminates less than it appears to.

**The route was identical and two things changed, not one: the filename and the
file's bytes.** R2 carries a prepended header block, so it is byte-identical in
*body* and a different file — different length, different hash. So the result is
consistent with *the name was the problem* and equally consistent with *something
about that exact file was the problem*.

**n=1 against a prior of two failures.** Suggestive, not settled, and the clean
version of the experiment would have been the original filename with the header
block added, or R2's filename with the body untouched.

Record it as suggestive with the confound named. This is the seventh instrument's
cousin: **a result that looks like a clean discrimination and is not, because the
experiment moved two things.** Worth having in the register precisely because the
conclusion is probably right — a correct conclusion from a confounded test is the
one nobody re-examines.

**Practical consequence: none.** The original is recovered, the exception is
recorded as one-time, and the next re-send keeps its filename. If it fails, we
have a cleaner trial.

---

## 2. 0002 — ACCEPTED

**The `(url, sha256)` reasoning is the best thing in the document**, and it is
the one I would not have caught:

> It discards the most useful thing an unchanged re-fetch tells you: the resource
> was *still* unchanged at a later moment. That is not a duplicate. It is a
> second observation, and it bounds the window in which a change did not happen.

That is the same move as *currency is a query, not a row*, applied to retrieval
rather than to facts. Both come from asking what the schema makes **unaskable**,
which is now twice the most productive question in this project.

**The changed payload as a retroactive falsification** is exactly right and it is
why a view is the correct instrument. It does not corrupt anything going forward;
it makes a claim about existing rows false. A constraint would have stopped us
recording the truth, and a trigger would have to decide at write time when the
only correct answer is to tell a human.

**And the detector stays quiet when nothing changed** — your own line about a
change detector that flags everything applies to itself, which is more than most
guards manage.

**The refusal to backfill, executed rather than asserted.** The sentence to keep:

> A comment saying so is a claim. A migration that stops rather than improvise is
> the property.

Three declined fabrications now — ticker `valid_from`, `sic_at_filing`, and an
invented fetch — and this is the first one that is **structurally impossible**
rather than merely declined.

**`record_fetch` first, same transaction**, on the asymmetry that a fetch row
without data is untidy while data without a fetch row is unprovenanced forever.
Correct, and the reasoning generalises to every ordering question of this shape.

**§7 accepted.** That *"still defensible" and "still true" had started doing
different work* is a better articulation of the habit argument than mine was.

---

## 3. OPEN-44 — what is hashed, and does it survive an archive?

**Establish before the first archive fetch. This is not a design objection; it is
a question the design does not yet answer.**

`fetch_log` hashes a payload per URL. That works cleanly for a small JSON
document. **It may not work at all for `submissions.zip`.**

A 1.4 GB archive rebuilt nightly will very plausibly differ byte-for-byte on
every download even when the data we care about is unchanged — zip member
ordering, embedded timestamps, compression differences. If so:

- `fetch_content_change` fires **every night**, on every archive fetch;
- the finding becomes routine, and **a finding that always fires is not a
  finding**;
- and it fires loudest on the source we just ruled as primary.

**The questions:**

1. Does the archive's hash actually change between downloads when its contents
   have not? Two fetches a day apart settle it.
2. If it does, is the right unit of hashing the **response**, or the **extracted
   member** — the per-filer JSON inside the archive, which is what a `filing` row
   actually derives from?
3. If it is the member, does `fetch_log` need a member identifier, or does a
   second table carry extraction?

**Do not answer this by making the view quieter.** Suppressing a detector that
fires correctly-but-uselessly is how a real signal gets lost; the fix is the unit
of measurement, not the threshold.

---

## 4. OPEN-45 — does provenance follow an update, or stay at creation?

`source_fetch_id` is `NOT NULL` on all three tables, which makes an
unprovenanced row unrepresentable. Good.

**But `filer.current_sic`, `current_name` and `metadata_as_of` are, by their
names, values that change.** When a later fetch updates them:

- if `source_fetch_id` stays at the row's creation fetch, **the column points at
  a fetch that did not produce the values it sits beside** — provenance that is
  present, non-null, and wrong;
- if it is updated in place, the record of which fetch created the row is lost.

**Either is defensible and the choice has to be made deliberately**, because the
failure mode of the first is the one this project keeps finding: a field that is
populated, passes every check, and misattributes.

Note that slice 1 may not have exercised this — a single ingest run creates rows
and never updates them, so the case arises on the **second** run against changed
metadata. **Establish whether the loader updates `current_*` at all**; if it
does, this is live, and if it does not, say so, because a `current_` column that
never updates is its own problem.

---

## 5. Everything else in D15 — accepted

OPEN-39 through OPEN-43 recorded as you have them. **OPEN-40 is the one I would
also flag hardest** — a flag named *previous report* reads as *stale, exclude
it*, a loader author filtering it would believe they were cleaning data, and
every test in 0001's verification would still pass because the rows it checks
would simply never arrive. The platform helping someone destroy the point-in-time
property is a novel shape and it belongs in doctrine.

`company_tickers.json` rejected for one question and adopted for another,
unchanged, with both rulings right: **a source is fit relative to a question,
never in itself.** That is the general form and it is worth more than either
ruling.

---

## 6. Sequence

**OPEN-39 next**, as you have it, then OPEN-40, 41, 42.

**OPEN-44 before the first archive fetch** — which is the run phase, so it is not
urgent, but it is cheaper to answer with two small fetches than to discover
during a 1.4 GB download.

**OPEN-45 whenever slice 1 is next opened**; it costs a read of the loader.

Run phase of 0001, 0002 and slice 1 gated as before: OPEN-25, OPEN-27, OPEN-30,
OPEN-21, OPEN-33.
