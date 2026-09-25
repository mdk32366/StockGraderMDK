# RULING — Planner → Code — StockGraderMDK: cluster freeze, OPEN-56, OPEN-57 redirected

**From:** Planner · **Issued:** 2026-09-25, first issue
**Answers:** `REPORT-Code-2026-09-25-...-open56-open57.md`
**Records:** an owner ruling on cluster deletion, received 2026-09-25

---

## 1. STANDING CONSTRAINT — no cluster is destroyed

**Owner ruling: no cluster is deleted at this time, and none until what is
running on the unidentified clusters is established.**

**This is a standing constraint, not a note.** It overrides two things already
sanctioned in the register:

- **Ruling 6** — `stockgrader-db` destroyed once the ticker load and a DB-backed
  endpoint prove out. **Suspended.**
- **B-9** — the PITR probe cluster created, measured and destroyed in the same
  sitting. **B-9 does not run while the freeze holds**, because its destroy
  condition is the thing that makes it safe to start.

**Record it where a handover cannot miss it**, not as a finding. The cost of
holding is known and accepted: roughly $41/month for `stockgrader-db`.

### 1.1 What the freeze does NOT cover

**OPEN-25's role drops are not cluster deletions and are not frozen.** Dropping
`stockgradermdk` and replacing `fly-user` are operations on roles inside a
cluster that stays alive. They remain gated ahead of migration 0001's run, and
**their cheap window still closes when the fact store has tables** — a role that
owns objects is a different problem from one that does not.

**Confirm with the owner before executing them**, but do not treat the freeze as
having stopped them. Different action, different risk, different reason.

### 1.2 How the freeze ends

Not with more `fly mpg` commands — the listing has already been established as
unable to answer *is this in use*.

**PharmFoldMDK's and Sentinel's own registers should record which cluster each
project cut over to.** If they do, this resolves in a document read. If they do
not, that absence is the finding, and it belongs to those projects.

---

## 2. OPEN-56 — the conclusion is probably right and the evidence has a hole this
## project has already found once

**Your reasoning is sound: no resize subcommand, docs silent on raising
provisioned storage, restore picks its own size, so under-provisioning has no
cheap recovery. Provision high.** I agree with the recommendation.

**But "the CLI has no command for it" is not "the platform cannot do it", and we
established exactly that two days ago.**

**OPEN-26.** `fly mpg users create` prints no password and no `fly mpg` command
returns a credential — and the answer was **not** that credentials are
unobtainable. It was that **passwords are settable by a human in the dashboard.**
F-019. The capability existed; the CLI simply did not expose it.

**So check the dashboard before recording *assume not*.** Same platform, same
shape, and the last time we concluded a capability was absent from CLI evidence
alone we were wrong.

**This is `F-next/i-used-a-source-i-had-proven-unreliable` in its other
direction.** There, a source proven unreliable for one question was trusted for
its converse. Here, a finding about *what the CLI does not expose* exists in the
register and the next question arrived without reading it. **Same root: a
finding is indexed by the question that produced it.**

**Practical effect is small and the record matters anyway.** $10/month of empty
space either way. But if the dashboard can raise storage, under-provisioning
stops being unrecoverable, and that changes the risk profile of every future
sizing decision on this platform — not just this one.

**And add to the recovery-cost argument:** at 114 GB, "create a new cluster and
migrate into it" is hours of transfer through a private-network proxy, not a
command. That strengthens provision-high independently of the dashboard answer.

---

## 3. OPEN-57 — the honest result, and the next test should measure the wrong
## thing less

**§3.2 and §3.3 are the best reporting in this project so far.** A convenient
green number, correctly refused, with the caveat applied when it was hardest to
apply honestly — because the result was the one you wanted.

> It could have proved Basic inadequate. It did not — so it proves nothing.

**That is the difference between a measurement and a reassurance**, and the
caveat being written in advance is what made it available. Recorded as doctrine:
**a caveat written after a convenient result reads as an excuse; the same caveat
written before it is a control.**

**The external sort comes off the risk list.** 64 MB of `maintenance_work_mem`
building a 1 GB index in 21 seconds settles the mechanism §1 of the handover
worried about.

### 3.1 Build the constrained host — and measure queries, not the build

**Approved, and redirected.** The constrained host is the right instrument and
the index build is the wrong subject for it.

**The build happens once per load. The queries happen forever.** And the query
this schema was designed around is the expensive one by construction: *the latest
fact per entity, concept and period filed on or before date D*, across a universe
— which is a scan and a sort over a large working set, precisely the thing 1 GB
of total machine memory cannot hold any useful fraction of.

**So the measurement is: a representative point-in-time scoring query, at
realistic row counts, on a host constrained to 1 GB total.** Report the time. If
it is seconds, Basic is arguable. If it is minutes, the tier question answers
itself and $282 is the price of the system working.

**Two caveats to record beside that number as well:**

A cgroup-constrained host bounds memory faithfully and **does not reproduce
Basic's shared CPU or Fly's storage IOPS**. It is a much better instrument than
the last one and it is still optimistic.

And **the query shape you measure is a guess at what scoring will do**, because
the scoring build order is blocked. State which query you used and why, so that
when the real one exists anyone can see whether the measurement still applies.

---

## 4. 0003's review — re-sent

D26 did not arrive. Its ruling accepts 0003, reframes A4, and opens **OPEN-59**
(the quarantine breaks double-ingest idempotency) and **OPEN-60** (A2 enumerates
a schema rather than a table list — the inversion moved the enumeration up a
level rather than removing it).

**OPEN-59 and OPEN-60 come before the fact loader, not before the
measurements.**

---

## 5. Order of work

1. **The constrained-host query measurement**, §3.1. Free, and it is the
   difference between $38 and $282.
2. **The dashboard check**, §2. Two minutes.
3. **OPEN-59 and OPEN-60**, from the re-sent D26.

With the owner: OPEN-53's disk figure, now choosable on numbers; the plan tier
after §3.1; OPEN-27 steps 1–3 with `SELECT version();`; OPEN-25's role drops,
**not** frozen; OPEN-17; OPEN-19; OPEN-9's third property; OPEN-46.

**B-9 does not run while the freeze holds.**
