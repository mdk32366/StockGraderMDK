# HANDOVER — Planner → Code — StockGraderMDK: final block before checkpoint

**From:** Planner · **Issued:** 2026-09-25, first issue
**Owner ruling:** this is the last work before a closeout and a context reset.

---

## 1. Scope — three items, and nothing else starts

**In:**

1. **B-9** — the PITR probe, refusal-first, per the consolidation's Part 3.
2. **OPEN-61** — the query plan and buffer scaling.
3. **OPEN-56** — the dashboard check on raising provisioned storage.

**Explicitly NOT in this block**, and each goes to the prework rather than being
half-started: OPEN-59, OPEN-60, the fact loader, OPEN-25's role drops, any
migration applied to a real database, and OPEN-27.

**If any of the three turns out to need a fourth thing, report it and stop.** The
purpose of the block is to reach a settled state, and a block that grows does not
reach one. This project has three consecutive reports saying *nothing built,
nothing half-built* — that is the state worth arriving at the checkpoint in.

---

## 2. B-9 — as specified, with one addition

Full terms are in `CONSOLIDATION-Planner-2026-09-25-...-D26-D29.md` Part 3:
control probe first at a timestamp predating the cluster, which **must** be
refused; confirm a refusal provisions nothing; coarse ladder oldest to newest;
stop at the first success; the resulting cluster named and recorded with the
freeze lifting as its end condition.

**Addition: cap the ladder.** If eight probes have not produced a success, stop
and report the bound reached. The finding is the boundary or the absence of one;
neither is worth an unbounded sequence of owner-at-the-keyboard commands on the
last block before a reset.

**Report against B-6's chain:** the PITR window and the oldest surviving full
backup together are the recovery horizon, and neither states it alone.

---

## 3. OPEN-61 — the plan, and whether reads scale with the table

The 882 ms query read approximately the whole table — 139,438 buffers, ~1.09 GB.
**The question is whether that is a property of the query or of the data volume.**

- The `EXPLAIN (ANALYZE, BUFFERS)` plan: seq scan or index, and if an index was
  available and rejected, why.
- **Buffer reads for one quarter against two.** If they roughly double, the
  working set is the table and no tier fixes it. If they stay flat, the tier
  question shrinks to nothing.

**That distinction decides whether the $244/month gap is a hardware problem or an
index problem**, and it is the single most useful number available before the
reset.

---

## 4. OPEN-56 — the dashboard

Whether provisioned storage can be raised after creation. Two minutes, and the
precedent is F-019: the CLI not exposing a capability is not the platform lacking
it, which is how we were wrong about credentials.

---

## 5. What to hand back

A single report covering all three, plus **the Builder's half of the closeout**:

- the register's current state — decisions ruled, open items with what each
  gates, findings
- what is built and unapplied: 0001, 0002, 0003, the runner, the EDGAR client,
  slice 1, 64 tests
- **what a new Builder context would need to know that is not in the register**,
  which is the part only you can write

I will write the Planner's half and the prework. **Together they are the
checkpoint**, and the next two windows start from them rather than from this
conversation.
