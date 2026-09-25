# REPORT — Code → Planner — StockGraderMDK: the fact loader is built and proven

**From:** Code (Builder) · **Issued:** 2026-09-25, first issue
**Executes:** the narrowed block's §3 path, items 1 and 2
**Branch:** `pr6-backup-strategy`, HEAD `a349713`, pushed
**Suite:** 64 → **92**, all green under this repository's own `.venv`
**Fly cluster mutations: NONE** · No money spent

**No delivery manifest accompanies this report.** The chain is retired, and this
document is committed to the repository rather than only handed across — see §7,
because the retirement's own reasoning only half applies until that is true.

---

## 1. What was built

Four commits, in order:

| | |
|---|---|
| `57a933b` | OPEN-59 and OPEN-60 closed, 6/6 red-test cases |
| `93750f7` | `tools/planner_index.py` — the archive index regenerates as part of the commit |
| `19127fe` | F-021, OPEN-63 — the credential in the transcript |
| `a349713` | **the FSDS fact loader + migration 0004**, 1,364 lines |

**The loader is the largest unbuilt piece on the critical path and it now
exists**, with `ingest/fsds.py`, `db/migrations/0004_coverage_window.sql`, 28
hermetic tests and an end-to-end proof harness.

---

## 2. OPEN-59 and OPEN-60 — closed, and one of them fought back

**OPEN-59.** `fact_collision` had **no constraint at all**, so re-ingesting a
quarter re-inserted every quarantined row. Identity is now the colliding key +
`value` + `source_ordinal`, and each term is load-bearing:

- **`value`** — two disagreeing rows must both insert. A5's property, now held
  by construction rather than by care.
- **`source_ordinal`** — three rows colliding where **two agree on value** must
  still yield three. **The harness confirms the wrong fix produces exactly 2.**
- **`source_fetch_id` deliberately excluded** — a re-ingest is a new fetch with
  a new id, so including it would **pass a naive idempotency test while fixing
  nothing.**

**A5 had to be repaired before that fix could exist.** It forbade any uniqueness
covering `concept` — a **proxy** for *would refuse a competing value*. The two
diverge at exactly one point: a constraint including `value` cannot refuse a
differing value. **A5 would have rejected the correct fix while permitting
nothing safer.** Recorded as **F-022**: a guard testing a proxy passes and fails
for the right reasons only while proxy and property agree, and the first case to
reach the divergence is likely to be **a correct change being refused** — which
reads as the guard working.

**OPEN-60.** A2 scoped its catalogue derivation to `nspname = 'public'`, so it
**enumerated a schema instead of a table list** — a table elsewhere escaped
exactly as `fact` escaped 0002's A5, one level up. Now scoped by excluding
system schemas. **`provenance_exempt` became schema-qualified in the same
change**, because widening the check while leaving the exemption unqualified
**moves the hole rather than closing it**.

**6/6 red-test cases, control green**, on a throwaway PostgreSQL 18.3 cluster.
`tools/redtest_0003.py` is committed, so the verdicts are reproducible rather
than reported.

---

## 3. The loader

**Refuses rather than coerces, and counts every refusal.** Co-registrant facts
(OPEN-39); unreadable dimensions — **refused, never defaulted to `'{}'`**,
because that asserts *no dimensions*, a different claim, and it would land in
0001's uniqueness key; rows with no value; facts whose filing is absent; and
collisions that disagree.

**`ON CONFLICT DO NOTHING` is used only after `partition_collisions` has removed
every disagreeing group.** Used without it, it is silent data loss — FSDS
violates its own documented key 32 times a quarter and **31 of those carry
different values**.

**Migration 0004 records the coverage window as DATA**, which was OPEN-51's
condition. `coverage_window` states the window in one query **including gaps**,
because a holed window reads exactly like a short one — the failure the ruling
names, arriving through the instrument built to prevent it.

---

## 4. Proven end to end, on a real database

Migrations applied through the runner against PostgreSQL 18.3, a synthetic FSDS
archive loaded, then **re-ingested under a NEW fetch**:

```
facts_seen 11 -> loaded 4 · coreg 1 · malformed 2 · unknown_filing 1
                 collapsed 1 · quarantined 2          accounting: BALANCED
both values kept   : -3123000 | 706000
dimensions stored  : {"ProductAxis": "WidgetMember"}
duration derived   : 2025-12-31..2026-03-31
re-ingest, new fetch: nothing moved
```

---

## 5. F-025 — the accounting constraint found a category nobody had named

`coverage_quarter` CHECKs that every fact seen was loaded, refused or
quarantined. **It refused the very first load: 11 seen, 10 accounted for.**

The gap was **exact duplicates** — rows sharing the key *and* agreeing on value.
Collapsing them loses nothing, which is exactly why the category was invisible:
it is neither a load, nor a refusal, nor a quarantine, and every counter in the
design was one of those three.

**So the constraint did not catch what it was written for.** It was written
against a silent drop. It caught **an incomplete taxonomy of outcomes** — the
counters were each correct and did not cover the space.

> **An arithmetic constraint over a set of counters tests something no
> individual counter can: that the categories cover the space.**

`collapsed_duplicates` is **derived** — `len(rows) - len(loadable) -
len(quarantined)` — rather than incremented in the loop, so it cannot drift from
the behaviour it describes. A counter in the loop would be a second
implementation of the same decision, free to disagree with the first.

**I would reasonably have shipped without that CHECK.** The counters were
individually correct. The gap would have shipped with them.

---

## 6. One thing I am NOT claiming

**The `segments` grammar is my reading, not confirmed against `readme.htm`.**

It is built to fail loud rather than quiet: a wrong grammar spikes
`refused_malformed` and the coverage row makes it visible, where a parser that
fell back to `'{}'` would write a confident, wrong *no dimensions* for every row
it could not read.

**That is a mitigation, not a verification**, and it should be confirmed before
the 45-quarter load. Flagged here rather than left to surface as a refusal rate
nobody expected.

---

## 7. Why this report is in the repository

The chain retired because the Planner can **read** `docs/planner/INDEX.md`. That
reasoning covers Planner → Code and says nothing about Code → Planner, which
still crosses the same lossy Downloads hop — **and D34's own correction was that
losses become impossible only after receipt.**

So Code reports are now committed under `docs/reports/` as well as delivered.
The argument for retiring manifests then applies symmetrically, rather than to
one direction while the other is assumed safe.

---

## 8. What is next, in order

**Blocking, and it is the owner's:**

1. **OPEN-27 steps 1–3** — the clean `schema_admin`. Nothing database-side moves
   without it. `stockgrader_app` is a `writer` and A-017 established a writer is
   refused `CREATE TABLE` **by design**.

**Then, and none of it needs a ruling:**

2. **Apply 0001–0004 to `stockgrader_scratch`** — settles the largest
   unvalidated assumption in the project. Four migrations, a runner and 92 tests
   have never met a Fly cluster.
3. **Confirm the `segments` grammar** against `readme.htm` (§6).
4. **Fetch one real FSDS quarter and load it.** First real rows. OPEN-33's
   acceptance test rides along: CIK 806085 present with filings ending 2008.
5. **Load the 45 quarters** — OPEN-51's measurement-first condition is now
   implementable because coverage is recorded as data.
6. **The first DB-backed endpoint.** Closes D-029's application half and moves
   recovery row 4 off `Never`.

**Still blocked, and not by infrastructure:** scoring, on §11.1 and §5.4. **P-13
is the finding that matters there** — deferred to "its own session" on day one,
no session ever scheduled. That is the critical path for the *application*, as
distinct from the store, and nothing built this sitting moves it.

**Carried, not done:** the recovery document's register edits — the freeze
narrowing, the cluster-naming requirement, P-12, P-13 — and **OPEN-63**, the
deferred credential rotation.
