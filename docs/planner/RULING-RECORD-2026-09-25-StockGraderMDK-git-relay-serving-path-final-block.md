# RULING RECORD — Owner → Planner → Code — StockGraderMDK: git relay, serving path,
# final block extended

**From:** Planner, recording owner rulings received 2026-09-25
**Issued:** 2026-09-25, first issue

---

## 1. The relay moves into git. RULED.

**Planner documents are committed to `docs/planner/` on receipt.**

**Mechanics:**
- Code commits each Planner document under its delivery number on arrival,
  unchanged, before applying it.
- **The manifest chain retires once this is working.** Not before — the last
  losses were found by it.

**What replaces the manifests, and it is better than counting:** the repository
is public through development under D-020, so **the Planner can read
`docs/planner/` directly from GitHub and see what landed.** Delivery verification
becomes observation rather than arithmetic against a stated expectation.

**Establish before retiring the chain:** that the Planner can actually fetch the
directory and file contents from the public repo. If it cannot, the chain stays
and we have learned something instead of assuming it — this is the same
CLI-is-not-the-platform caution that OPEN-56 needed.

**What this does and does not fix.** It makes the record durable after receipt:
nothing committed can be lost, and both sides can see the same state. **The
Planner→owner→Code hop is still a hop** — a document that never reaches Code is
still never committed. But it is the last remaining gap rather than the whole
channel, and it is visible immediately rather than two deliveries later.

---

## 2. OPEN-62 — RULED: scored, stacked, tracked

**The API serves precomputed scores to a consuming application. Nothing computes
on request, and nothing serves from the fact store.**

**Consequences, in order of how much they change:**

**2.1 — The tier question largely dissolves.** The 114:1 ratio applies to a
quarterly batch nobody waits on, not to a request path. A four-hour batch on
Basic is unremarkable, and your zero OOM kills under continuous reclaim is real
evidence the batch survives. **OPEN-61 keeps its value anyway** — if the working
set scales with the table, that is an index problem no tier fixes, and it will
show up in batch runtime rather than in request latency.

**2.2 — "Tracked" means score history, which means a scores table, which means
0004.** Not in this block. Named so the checkpoint carries it.

**2.3 — And it has the fact store's exact problem, one level up.**

A score is *for* an as-of date and *computed at* a point in time under a model
version. **Those are two dates and a version, and collapsing them is the
restatement trap in new clothing.**

If recomputing 2019's score under an improved GQS overwrites the row, then a
backtest reads scores that were never produced at the time, and every validation
silently measures today's model against history — **the same lookahead the TDD
rejects for restated financials, arriving through the output rather than the
input.**

**So the scores table wants the same shape as `fact`:** keyed on as-of date **and
the computation that produced it**, append-only, with currency as a query rather
than a row. *The current score for ticker X* is not a row — it is the latest
computation for the latest as-of date, and a query can be asked *as of when, and
under which model*.

**This is a design constraint on 0004, recorded now rather than discovered
after a recompute.** It is cheap now and impossible later, which is the fourth
time that sentence has applied.

---

## 3. Final block extended. RULED.

**Added: get the migrations onto the live cluster.**

1. **OPEN-27 steps 1–3**, with `SELECT version();` folded in — create the clean
   `schema_admin`, set its password in the dashboard, store it, **prove it** by
   connecting and running DDL in scratch. Report before step 4.
2. **Apply 0001, 0002 and 0003 through the runner against
   `stockgrader_scratch`** on `kzpwm0j1dm204nv3`. Canary-marked, disposable,
   `stockgrader` untouched.

**What this settles as a side effect:** OPEN-30 (the server's major version),
OPEN-21 (whether the runner works through the endpoint it gets), and **the
largest unvalidated assumption in the project** — that three migrations, a
runner and 64 tests proven on deleted local clusters apply on the platform.

**Report before proceeding past OPEN-27 step 3.** That is where unrecoverable
actions would begin, and none are in this block.

**The block is now four items and closes:** B-9, OPEN-61, the OPEN-56 dashboard
check, and this. **Nothing else starts.** OPEN-59, OPEN-60, the fact loader,
OPEN-25's drops and any migration against `stockgrader` all go to the prework.

---

## 4. Cluster evaluation — after the Fly instance is up. Prework.

The owner's sequence: get the instance running, **then** evaluate which clusters
are valid and which are surplus.

**The destruction freeze holds until that evaluation happens.** Anything built
meanwhile is named and recorded with a stated end condition, per the standing
requirement — including B-9's probe cluster.

**The evaluation is not a `fly mpg` task.** The listing cannot answer *is this in
use*; PharmFoldMDK's and Sentinel's own registers should record which cluster
each project cut over to. **That is the first thing to look at, and if those
registers do not answer it, the absence is the finding.**

---

## 5. Checkpoint contents, unchanged

Builder's half: register state, what is built and unapplied, and what a new
Builder context needs that is not in the register.

Planner's half plus the prework: ruled decisions **with their conditions
attached**, open items with what each gates after the sweep, the Planner error
record and the rules it produced, the doctrine, and the two sessions that are not
database work — **§11.1's R&D ruling and the §12 port of GQS v3 to v4 grounded on
this repo.**
