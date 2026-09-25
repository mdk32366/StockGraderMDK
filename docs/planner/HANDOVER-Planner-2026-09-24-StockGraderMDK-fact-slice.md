# HANDOVER — Planner → Code — StockGraderMDK: the fact slice

**From:** Planner · **Issued:** 2026-09-24, first issue
**Answers:** `REPORT-Code-2026-09-24-...-open39-42-established.md`
**Source ruling:** OPEN-36 — Financial Statement Data Sets, **on the dimensions
evidence alone** (60.7%). The per-fact-entity pillar is withdrawn, per §2.2 of
your report.

---

## 1. Rulings on the establishments

**OPEN-39 — possibility (3). ACCEPTED, and your framing of it is better than my
question was.** I asked for the mapping's failure rate; you answered that **there
is no rate because there is no domain** — 93.8% of carrying submissions have no
`aciks` at all, and a third of the rows use filer-internal codes that nothing
external could ever resolve. A failure rate implies a mapping that sometimes
works. This one does not exist.

**Co-registrant facts are REFUSED. RULED**, per the scheme rule slice 1 proved.

**§2.3 is the paragraph I would keep, and you were right not to bury it.**
`entity_cik` trivially equal to the filer's CIK is the exact condition that
disqualified companyfacts. The distinction — a refusal we chose and can count,
versus a silence we could not detect — is real and is not a rationalisation. But
record it with the part that is uncomfortable intact: **the schema still cannot
be contradicted by ingested data**, and A8 plus the fixture remain the only
evidence for OPEN-29's fix.

**OPEN-40, 41, 42 — accepted as established.**

§4's note is the methodological point of the day: the distribution corroborates
*because* the derivation came from documentation first. Inferred from samples,
the distribution would have agreed with whatever was inferred. That is the
eighth instrument — a confirmation that cannot disconfirm.

**OPEN-42's nominal-versus-usable distinction stands as a property, not a
filter** — see §4.3.

---

## 2. Scope

**In:** `num.txt` and `sub.txt` from FSDS quarterly archives → `fact` rows.

**Out:** anything scoring-shaped; TTM assembly; concept normalization (the
revenue tag priority list and everything like it) — that belongs in views, per
0001's *ingestion stays dumb*.

---

## 3. The integration question, which is also a cross-check

**`filing` is owned by slice 1, from `submissions.zip`. The fact slice reads it
and does not write it.**

`fact.accession` has an FK to `filing`. So a fact whose `adsh` has no `filing`
row **is refused**, and the refusals are counted and reported.

**That turns an integration problem into a measurement.** Every FSDS `adsh`
should exist in `submissions.zip` — both are SEC products describing the same
filings. **A non-trivial refusal rate is a finding about one of the two sources**,
and it is a cross-check we get for free by not letting the fact slice create
filing rows to paper over the gap.

**Run-phase precondition:** slice 1's load must have completed for at least the
coverage window the fact slice is ingesting. Otherwise the refusal rate measures
our own sequencing rather than the sources.

---

## 4. Field mapping — established, not assumed

**4.1 Settled by your establishments:**

| 0001 column | FSDS |
|---|---|
| `period_end` | `ddate` |
| `period_type` | `'instant'` if `qtrs = 0`, else `'duration'` |
| `period_start` | `ddate` when instant; `ddate` minus `qtrs` quarters otherwise |
| `unit` | `uom` |
| `entity_cik` | the filer's CIK; rows carrying `coreg` are refused |

**4.2 Three things to establish before building. Do not infer these from
samples** — §1's point applies to each.

**OPEN-48 — what does `version` contain, and what happens to filer extension
tags?** `taxonomy` and `concept` come from `version` and `tag`. Standard concepts
presumably carry a taxonomy identifier. **Custom extension tags are the
question:** what does `version` hold for them, are they distinguishable from
standard ones by inspection, and how many are there? GQS scores standard
concepts; extensions are noise for scoring and **must not be silently dropped**,
because a filer that tags revenue with an extension would simply go missing
rather than be visibly excluded.

**OPEN-49 — is `segments` ever truncated, and what happens when it is?**
`segments` becomes `dimensions` jsonb, which is a **parse**, not a copy. If the
field has a length limit, a truncated string parsed into jsonb yields a
**well-formed dimension that is wrong** — and it would join, filter and group
like a real one. Establish the limit and the truncation rate. A parse failure
must refuse the row, not default to `'{}'`, because `'{}'` means *consolidated*
and silently promoting a segment fact to consolidated is the worst available
outcome.

**OPEN-50 — is `sub.txt.adsh` formatted identically to slice 1's accession?**
The FK depends on it. A dash-formatting difference would make the refusal rate
100% and look like a source disagreement.

**4.3 `prevrpt` and coverage — store, never filter.**

`prevrpt` is recorded on the submission and **never used to exclude**. It marks
the original that was later amended, which is exactly the value that was knowable
at the time.

**The same rule governs coverage.** Ingest from the archive's nominal start;
record per-quarter row counts; **do not truncate at 2011q4.** The usable-start
boundary is a property the validation layer applies and states in its own output,
not a filter baked into the data. This project has now arrived at *store, don't
filter* four times — `prevrpt`, dimensions, superseded facts, and coverage — and
it is worth recording as the general rule rather than as four instances.

**4.4 `sic_at_filing` stays NULL.** OPEN-37 is unanswered — whether `sub.txt.sic`
is as-filed or as-of-extract — and that distinction is the entire reason the
column exists.

---

## 5. OPEN-51 — the sizing question, and it needs the owner

**This is the item to resolve before building, and it is the reason this handover
does not simply say "ingest everything."**

2026q2 alone holds **3,608,711 rows**. Across roughly sixty quarters from 2011q4,
a full-history load is plausibly **well over a hundred million fact rows**.
**The live cluster's disk is 15 GB** — a figure that arrived by a silent restore
resize nobody asked for (OPEN-22).

**I have not estimated bytes per row and will not guess.** Measure it: load one
quarter into a local cluster, take the table and index sizes, and multiply.
That number decides the rest of this section, and it is an hour's work against a
choice that is expensive to unmake.

**If it does not fit, the resolution is to narrow by concept, not by dimension —
and the reason is specific rather than aesthetic.**

The ceiling argument that ruled out companyfacts was that **the source never had
the data**, so the loss was permanent. **FSDS quarterly archives are immutable
once published and re-downloadable indefinitely.** A narrow ingest is therefore
**reversible**: the concepts GQS needs are derivable from the TDD's §4 blocks,
and widening later means re-reading an archive that has not changed.

**That asymmetry does not hold for dimensions.** Filtering `segments` at ingest
would discard the 60.7% that is the entire basis of OPEN-36 — recoverable in
principle, but it would mean the ruling bought nothing in practice and the store
would be indistinguishable from the companyfacts one we rejected.

**So the order of preference, if sizing forces a choice:**

1. Narrow the **concept** set to what §4's blocks require, plus a margin.
2. Increase the disk.
3. **Not** narrowing dimensions.

**Owner's ruling**, once the measurement exists. Report the number and the
options; do not choose.

---

## 6. OPEN-44 — the answer differs by source, and it matters here

`submissions.zip` rebuilds nightly, so its hash may churn without its content
changing — that is the noise case, and it belongs to slice 1.

**FSDS quarterly archives should be immutable once published.** So on this
source, `fetch_content_change` firing is **high-signal**: a published quarter
changing is the SEC having restated an archive, which is exactly the event
D-023's re-derivability claim is about, and it would falsify every fact row
loaded from the superseded copy.

**Establish it cheaply:** fetch a quarter's archive twice and compare hashes. If
FSDS is stable and `submissions.zip` is not, that is the answer to OPEN-44 and it
is per-source rather than global.

---

## 7. What to prove, and what not to claim

**Prove:** the period derivation on a fixture covering `qtrs` of 0, 1, 2, 3, 4
and 5, with the instant case landing on `period_start = period_end`. An
off-by-one-quarter error here is silent and poisons every growth metric in §4.1.

**Prove:** a `coreg`-carrying row is refused and counted, not coerced.

**Prove:** a malformed `segments` value refuses the row rather than defaulting
to `'{}'`.

**Prove:** double-ingest idempotency against `fact_one_per_filing`, as slice 1
proved its own.

**Do not claim** this exercises A8. `entity_cik` is the filer's CIK on every
ingested row by construction. That is stated in the ruling and should be stated
again in the report, because it is the kind of thing a green suite quietly
implies.

---

## 8. Sequence

OPEN-48, 49, 50 and the §5 measurement first. **Report before building** —
§5 needs an owner ruling and §4.2's answers change the loader's shape.

Run phase gated as before: OPEN-25, OPEN-27, OPEN-30, OPEN-21, OPEN-33, plus
slice 1's own run per §3.
