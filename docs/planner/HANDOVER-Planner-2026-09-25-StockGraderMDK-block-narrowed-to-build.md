# HANDOVER — Planner → Code — StockGraderMDK: the block is narrowed to what builds

**From:** Planner · **Issued:** 2026-09-25, first issue
**Supersedes:** `HANDOVER-Planner-2026-09-25-...-final-block-before-checkpoint.md`
and §3 of `RULING-RECORD-2026-09-25-...-git-relay-serving-path-final-block.md`
**Owner ruling, 2026-09-25**

---

## 1. Three of the four items are deferred, and the reversal is the point

The final block was B-9, OPEN-61, the OPEN-56 dashboard check, and getting the
migrations onto the live cluster. **Only the last one builds anything.**

**Deferred to the prework:**

- **B-9** — measures a recovery window. Real value, no urgency, and under the
  freeze it now leaves a retained cluster.
- **OPEN-61** — measures a query plan to decide a tier. **The owner has ruled
  that money is not the blocker, so it was measuring a decision already made.**
- **OPEN-56 dashboard check** — two minutes, and it can ride along with any
  future dashboard visit.

**This reverses the block I issued an hour earlier.** That is deliberate: those
three are paperwork wearing a measurement's clothes, and the project has spent
three days learning to tell the difference.

**`F-next/a-measurement-that-decides-nothing`:** a measurement is only worth its
cycle if some decision changes on the result. OPEN-61's did not — the owner had
already removed the constraint the measurement existed to price. **Before
proposing a measurement, name the decision it changes and check that the decision
is still open.**

---

## 2. What the block is now

**One item: get a schema onto the real cluster.**

**2.1 — OPEN-27 steps 1 to 3**, with `SELECT version();` folded in (OPEN-30).
Create the clean `schema_admin`, set its password in the dashboard, store it in
the password manager, and **prove it** — connect, run DDL in scratch, drop what
you made. **Report before step 4.** That is where unrecoverable actions would
begin and none are in this block.

**2.2 — Apply 0001, 0002 and 0003 through the runner against
`stockgrader_scratch`** on `kzpwm0j1dm204nv3`. Canary-marked, disposable,
`stockgrader` untouched.

**What this settles:** OPEN-30, OPEN-21 for the runner, and **the largest
unvalidated assumption in the project** — three migrations, a runner and 64 tests
proven only on local clusters that were then deleted.

---

## 3. Then the path to something that exists

Stated so the next block does not need a handover to find:

1. **OPEN-59 and OPEN-60** — the quarantine's double-ingest idempotency, and
   A2's schema scope. Both small, both already specified.
2. **The fact loader**, on the ruled FSDS sources, with the establishments from
   OPEN-48/49/50 already in hand.
3. **Load the 45 quarters.** Rows in a real database.
4. **A DB-backed endpoint.** This is the one that pays: it closes D-029's
   application half, moves recovery row 4 off `Never` for the data half, and
   makes the gate able to notice a staged secret for the first time.

**None of that is blocked by the checkpoint.**

---

## 4. What is genuinely blocked, and it is not infrastructure

**Scoring.** §11.1 has been undated since day one (P-13), and GQS v3 needs
porting to v4 before a build order can issue (ruling 8). **Neither is database
work and neither has been scheduled.**

Until they happen, the loader delivers into a store nothing reads. **Those two
sessions are the critical path for the application**, as distinct from the
infrastructure, and the prework exists mainly to prepare them.

---

## 5. Standing constraints, unchanged

**No cluster is destroyed.** Building is unrestricted; anything built is named
and recorded with a stated end condition.

**INDEX.md is regenerated as part of the commit that adds documents, never
separately.** A stale index is indistinguishable from a complete one, and it is
now the only door. If that cannot be automated, the manifest chain does not fully
retire — a hand-maintained index is a manifest with extra steps.

**The manifest chain is otherwise RETIRED.** D33's end condition is met: the
Planner has read `docs/planner/INDEX.md` and every document links from it. 79
issued, 79 present, the first agreement of those figures in the project.
