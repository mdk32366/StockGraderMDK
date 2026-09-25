# RULING — Planner → Code — StockGraderMDK: B-9 runs, restructured for the freeze

**From:** Planner · **Issued:** 2026-09-25, first issue
**Supersedes:** §2 of
`RULING-Planner-2026-09-25-...-freeze-narrowed-orders-reissued.md`

---

## 1. B-9 is run. My reading was backwards.

The owner wants the PITR probe. D28 §2 recorded it as parked, which was my
inference from a one-word answer — **the correction costs a line because the
inference was flagged as one**, which is the only reason worth mentioning it.

---

## 2. The original shape assumed a destroy, and it cannot have one

B-9 was written as **create, measure, destroy, in the same sitting** — the
destroy being the condition that made it safe to start, precisely because of the
two clusters next door.

**Under the destruction freeze that clause cannot be honoured.** So the probe
must be restructured rather than run as written, and the restructuring is
straightforward: **make the refusals do the work.**

---

## 3. Refusal-first — probe so that most attempts create nothing

**A PITR restore inside the window creates a cluster. One outside the window is
refused.** A refusal is the cheap outcome and it is also the informative one,
because the boundary is what we are trying to find.

**3.1 — Control first, and this is not a formality.** Probe a timestamp
**before `kzpwm0j1dm204nv3` existed** — the cluster was restored on 2026-09-23,
so anything on the 22nd or earlier is outside any possible window.

**That must be refused.** If it is not, the instrument is lying and every later
result is worthless. *A check must be capable of failing before trying to make it
fail means anything* — the doctrine applies to this probe as much as to a SQL
assertion, and a control probe is what makes the refusals evidence rather than
absence.

**3.2 — Establish that a refusal is free.** The first refusal should error
**before provisioning anything**. Confirm that — `fly mpg list` before and after.
If a refused PITR restore leaves a cluster behind, stop and report: the whole
structure below depends on it, and that is a finding either way.

**3.3 — Then walk forward on a coarse ladder.** Oldest to newest, each refusal
free, each one raising the known lower bound. **Stop at the first success.**

The boundary is then bracketed between the last refusal and that success, and
the resolution is the ladder spacing — **so choose spacing such that one success
is enough.** Half-day steps over the cluster's short life will do; there is no
value in bisecting to the minute.

**3.4 — At most one cluster is created**, and only by the first success.

---

## 4. The cluster that results is retained and recorded

Per D28 §3, since nothing can be destroyed:

- **`-n` name saying what it is.** Something like `stockgrader-pitr-probe` —
  identifiable by reading, which is the distinction the two unidentified clusters
  fail.
- **Register line: who built it, why, and what ends it.** **What ends it: the
  destruction freeze lifting.** A retained cluster with no stated end condition
  is an orphan with a birth certificate.
- **Cost, accepted and recorded:** roughly $38/month plus storage until the
  freeze lifts. Note that `restore` sizes clusters itself — it produced 15 GB
  from a 10 GB source (OPEN-22) — so the storage figure is not ours to choose.

---

## 5. What the probe is for, restated so the result is interpretable

`--pitr-time` requires a recovery window **no command reports**. That is
`F-next/pitr-available-window-invisible`, and it is F-015's shape: a capability
that looks available until it is load-bearing.

**The finding is the measured boundary**, and a refusal names it as usefully as a
success. Report the ladder, every refusal with its timestamp, the first success,
and the bracket.

**And report what the boundary means against the backup chain.** B-6 established
that retention is *chains with a living root*. If the PITR window and the oldest
surviving full backup disagree, that gap is the real recovery horizon and neither
number alone states it.

---

## 6. Order of work, updated

1. **B-9**, per §3. Owner at the keyboard, one command at a time — the restore is
   still marked as a precaution, though it has now twice printed only ID and name.
2. **The constrained-host query measurement** — free, and may settle the tier.
3. **The dashboard check on OPEN-56.**
4. **A real Basic cluster**, only if 2 is inconclusive.
5. **OPEN-59 and OPEN-60**, before the fact loader.

Unchanged: no cluster is destroyed; ruling 6's destroy stays suspended; OPEN-25's
role drops are not frozen and their cheap window closes when the fact store has
tables.
