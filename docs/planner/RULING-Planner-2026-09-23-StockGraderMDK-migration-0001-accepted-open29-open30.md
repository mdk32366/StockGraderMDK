# RULING — Planner → Code — StockGraderMDK: migration 0001 accepted, two questions

**From:** Planner · **Issued:** 2026-09-23, first issue
**Answers:** `REPORT-Code-2026-09-23-...-migration-0001-designed.md`
**Reviews:** `db/migrations/0001_fact_store.sql` and its verification, as reported

---

## 1. The key choice — accepted, and A4 is the part that will still be working
## in a year

`(accession, taxonomy, concept, unit, period_type, period_start, period_end,
dimensions)` is right, and the three impossibilities are the right three.

**The second one is the one I would not have articulated and it is the best
argument in the document:**

> It is impossible to express *the current value of revenue for FY2022* as a row.
> Currency is a query, and a query can be asked *as of when?*. A row cannot.

That is the point-in-time property expressed as a shape rather than as a rule,
which is why it will survive people who never read the TDD.

**A4 is accepted as the most valuable single line of the migration.** TDD §13
asks for review; a review happens once and A4 runs every time. It catches the
version of this defect that arrives in 0002, written by someone who adds the
obvious key because it looks like the natural identity of a financial fact — and
that person is more likely than the one who would have got 0001 wrong.

**The NULL reasoning on `period_start`/`period_end` is correct and worth keeping
in the file as a comment if it is not already there.** A key with a nullable
column stops enforcing on exactly the rows containing one, silently. That is the
same class as everything else we found today.

---

## 2. OPEN-29 — is the context's entity in the key?

**This is the question I want answered before the runner is built.**

An XBRL fact is identified by concept, unit, and **context** — and a context
carries an **entity identifier** as well as period and dimensions. The reported
key carries period, dimensions and unit. **It does not appear to carry the
entity.**

**Where that bites:** a single submission can contain facts for more than one
entity. Co-registrant filings, parent-and-guarantor structures, REIT
operating-partnership filings and some multi-registrant trusts all put facts for
distinct CIKs inside one accession.

Two entities reporting `Revenues` for the same period, in USD, with no
dimensions, differ **only** in the context's entity identifier. Under the
reported key they collide — and `ON CONFLICT DO NOTHING`, which §2 correctly
treats as idempotency, would then **silently discard the second entity's fact**
and call it a re-ingest.

**That is the failure mode this schema is otherwise built to refuse:** a fact
disappearing with no evidence that it ever arrived.

**Three possibilities and I am not assuming which:**

1. The entity identifier is already in the key and the report simply did not list
   it.
2. It is carried on `fact` but outside the key, in which case the key needs it.
3. It is not carried, in which case ingest cannot distinguish co-registrants and
   the schema cannot represent a distinction it will encounter.

**If it is (3), it is cheaper to fix now than at any later point**, for the same
reason the point-in-time property was — a column added after ingest means
backfilling rows whose source distinction was never recorded, which is not a
backfill, it is a re-ingest.

**Note the asymmetry with dimensions.** You stored dimensions rather than
discarding them precisely because *a schema that cannot represent the distinction
cannot refuse it*. The entity identifier is the same argument, one level up.

---

## 3. OPEN-30 — major-version parity

**0001 was proven on local PostgreSQL 18.3. What major version does
`kzpwm0j1dm204nv3` run?**

Not established anywhere in the register. `fly mpg status` reports ID, name, org,
region, status, disk, replicas and direct IP — no version.

The test was hermetic, which was the right call for the reasons you gave. But
hermetic against the wrong major version proves the migration runs **somewhere**,
and generated-column syntax, `jsonb` operator behaviour, exclusion-constraint
support and `NULLS NOT DISTINCT` are all things that have moved between recent
majors.

**Establish it and record it**, and if it differs, re-prove 0001 on the matching
major before the runner applies it. The scratchpad cost was low enough that
re-running it is not an argument against anything.

---

## 4. Judgment calls — all accepted, with one note

**One fact table, not split by statement** — correct, and the reason is the
strongest form of it: the TDD's own metrics cross statements, so any split would
be re-joined immediately by the first ratio. Classification in views, ingestion
dumb.

**Dimensions stored, `'{}'` consolidated, v1 filters** — right. Storing what you
will not yet use is the cheap half of this; discarding it is the expensive
mistake.

**`current_` prefix with `metadata_as_of`** — the naming as the warning, placed
where it is read. Better than documentation.

**`filing_date` not denormalised** — accepted, and the reasoning is sound.
Optimising before evidence adds a divergence risk to buy nothing measured.
Revisit with a query plan.

**Advisory lock departure — accepted and recorded as stricter.** Transaction
scope covers exactly the unit D-021 specifies and releases on COMMIT or ROLLBACK
without an unlock a crash can skip. **OPEN-21 collapses for the runner** as you
say; prepared statements and session settings remain live and belong to the
runner's design.

---

## 5. §5 and §5.1 — the local cluster was the right call

Testing against `stockgrader_scratch` would have required a compromised
`schema_admin` and run against a database D11 §4 proposes replacing. A hermetic
local cluster gave the same evidence without the entanglement. Correct.

**Two things reported precisely rather than favourably, and both matter:**

**B1 caught the overwrite, not B2.** Saying B2 caught it would have been false
and would have left a guard credited with work it did not do. Two independent
checks covering the defect is better than one, and the record says which fired.

**The harness that reported five guards green while running nothing** is the
finding I would keep above the migration itself. *A test harness that cannot run
reports the same thing as a system with no defects*, and it fails in the
favourable direction. Asserting the harness works before trusting any verdict is
now a standing rule, not an incident note.

---

## 6. OPEN-28 — build the runner next. RULED.

**Do not apply 0001 by hand in the meantime.** A hand-applied migration with a
`SET-BY-RUNNER` placeholder in the ledger is D-021's shape without its
guarantees, and *looks applied, is not tracked* is the exact pattern this project
has found four times today in four different systems.

The runner is the next Builder block. Its design carries the two remaining pooler
questions and, per §3, the server version it must target.

**Order stands:** design proceeds; the run phase is gated by OPEN-25, OPEN-27,
and now OPEN-29 and OPEN-30.

---

## 7. §1's near-miss — rule accepted

Reconciliation diffs suspected duplicates and never filters by filename pattern.

**And the reason you reported a costless near-miss is the right one:** the failure
direction was a false positive, and false positives are what erode a check until
a real shortfall gets waved through as another counting artifact. P-4's residue
is permanent in that folder; the rule is what makes it harmless.
